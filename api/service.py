from typing import Optional, List, Callable, Type

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from geoalchemy2.functions import ST_Intersects, ST_Transform, ST_GeomFromEWKT, ST_Contains, ST_IsValid, ST_X, ST_Y
from sqlalchemy import select, Select, func, text, Row
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql import operators
from sqlalchemy.sql.functions import GenericFunction
from sqlean import OperationalError

import database
import models
import schemas

# FastAPI has very poor support for nested types
# Build jsonb in order to avoid N+1 and deserialization problems
_county_object = func.json_object(
    text("'code', counties.code"),
    text("'name', counties.name"),
    text("'feature_id', counties.feature_id"),
    text("'area_ha', counties.area_ha"),
    type_=JSONB,
).label("county")

_municipality_object = func.json_object(
    text("'code', municipalities.code"),
    text("'name', municipalities.name"),
    text("'feature_id', municipalities.feature_id"),
    text("'area_ha', municipalities.area_ha"),
    "county", _county_object,
    type_=JSONB,
).label("municipality")

_flat_residential_area_object = func.json_object(
    text("'code', residential_areas.code"),
    text("'name', residential_areas.name"),
    text("'feature_id', residential_areas.feature_id"),
    text("'area_ha', residential_areas.area_ha"),
    type_=JSONB,
).label("residential_area")

_residential_area_object = func.json_object(
    text("'code', residential_areas.code"),
    text("'name', residential_areas.name"),
    text("'feature_id', residential_areas.feature_id"),
    text("'area_ha', residential_areas.area_ha"),
    "municipality", _municipality_object,
    type_=JSONB,
).label("residential_area")

_flat_street_object = func.json_object(
    text("'code', streets.code"),
    text("'name', streets.name"),
    text("'full_name', streets.full_name"),
    text("'feature_id', streets.feature_id"),
    text("'length_m', streets.length_m"),
    type_=JSONB,
).label("street")


class InvalidRequestGeometry(Exception):
    def __init__(self, message: str, field: str, value: str):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class GeomFromEWKB:
    pass


def _get_filter_func(filter_method: schemas.GeometryFilterMethod) -> type(GenericFunction):
    match filter_method:
        case schemas.GeometryFilterMethod.intersects:
            return ST_Intersects
        case schemas.GeometryFilterMethod.contains:
            return ST_Contains
        case _:
            raise ValueError(f"Unknown geometry filter method: {filter_method}")


class BoundaryService[S, G]:
    model_class: type[models.BaseBoundaries]
    base_columns: List[InstrumentedAttribute]
    select_func: Callable[[List[InstrumentedAttribute]], Select]

    def __init__(
            self,
            model_class: type[models.BaseBoundaries],
            additional_select_columns: List[InstrumentedAttribute],
            select_func: Callable[[List[InstrumentedAttribute]], Select]
    ):
        self.model_class = model_class
        self.select_func = select_func
        self.base_columns = [
            model_class.name,
            model_class.code,
            model_class.feature_id,
            *additional_select_columns
        ]

    def get_without_geometry(self, db: Session, code: str) -> Optional[Type[S]]:
        query = self.select_func(self.base_columns)
        query = query.filter(self.model_class.code == code)

        return db.execute(query).first()

    def get_with_geometry(
            self,
            db: Session,
            code: str,
            srid: int,
    ) -> Optional[Type[G]]:
        query = self.select_func(
            [
                *self.base_columns,
                ST_Transform(self.model_class.geom, srid).label("geometry"),
            ]
        )
        query = query.filter(self.model_class.code == code)

        return db.execute(query).first()

    @staticmethod
    def _is_valid_geometry(db: Session, geom: GenericFunction) -> bool:
        try:
            return db.execute(ST_IsValid(geom)).scalar() == 1
        except OperationalError:
            return False

    def _filter_by_geometry(
            self,
            db: Session,
            query: Select,
            geom_value: str,
            field: str,
            filter_func_type: type(GenericFunction),
            geom_from_func_type: type(GenericFunction),
    ):
        geom = ST_Transform(geom_from_func_type(geom_value), 3346)
        if not self._is_valid_geometry(db, geom):
            raise InvalidRequestGeometry(message="Invalid geometry", field=field, value=geom_value, )

        return query.where(filter_func_type(geom, self.model_class.geom))

    def _filter_by_geometry_filter(
            self,
            db: Session,
            query: Select,
            geometry_filter: schemas.GeometryFilter
    ) -> Select:
        filter_func_type = _get_filter_func(geometry_filter.method)

        if ewkb := geometry_filter.ewkb:
            query = self._filter_by_geometry(
                db=db,
                query=query,
                field="ewkb",
                geom_value=ewkb,
                filter_func_type=filter_func_type,
                geom_from_func_type=database.GeomFromEWKB,
            )

        if ewkt := geometry_filter.ewkt:
            query = self._filter_by_geometry(
                db=db,
                query=query,
                field="ewkt",
                geom_value=ewkt,
                filter_func_type=filter_func_type,
                geom_from_func_type=ST_GeomFromEWKT,
            )

        if geojson := geometry_filter.geojson:
            query = self._filter_by_geometry(
                db=db,
                query=query,
                field="geojson",
                geom_value=geojson,
                filter_func_type=filter_func_type,
                geom_from_func_type=database.GeomFromGeoJSON,
            )

        return query

    def _filter_by_name(self, query: Select, name_filter: schemas.NameFilter) -> Select:
        if name_filter.contains:
            query = query.filter(self.model_class.name.icontains(name_filter.contains))
        if name_filter.starts:
            query = query.filter(self.model_class.name.istartswith(name_filter.starts))

        return query

    def search(
            self,
            db: Session,
            sort_by: schemas.SearchSortBy,
            sort_order: schemas.SearchSortOrder,
            geometry_filter: Optional[schemas.GeometryFilter],
            name_filter: Optional[schemas.NameFilter],
            codes: Optional[List[str]],
            feature_ids: Optional[List[int]],
    ) -> Page[Type[S]]:
        query = self.select_func(self.base_columns)

        if geometry_filter:
            query = self._filter_by_geometry_filter(db, query, geometry_filter)

        if name_filter:
            query = self._filter_by_name(query, name_filter)

        if feature_ids and len(feature_ids) > 0:
            query = query.filter(self.model_class.feature_id.in_(feature_ids))

        if codes and len(codes) > 0:
            query = query.filter(self.model_class.code.in_(codes))

        sort_by_field = operators.collate(getattr(self.model_class, sort_by), "NOCASE")

        if sort_order == schemas.SearchSortOrder.desc:
            sort_by_field = sort_by_field.desc()

        query = query.order_by(sort_by_field)

        return paginate(db, query, unique=False)


county_service = BoundaryService[schemas.County, schemas.CountyWithGeometry](
    model_class=models.Counties,
    additional_select_columns=[
        models.Counties.area_ha,
    ],
    select_func=lambda columns: select(*columns).select_from(models.Counties),
)

municipalities_service = BoundaryService[schemas.Municipality, schemas.MunicipalityWithGeometry](
    model_class=models.Municipalities,
    additional_select_columns=[
        models.Municipalities.area_ha,
        _county_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Municipalities, models.Municipalities.county
    ),
)

elderships_service = BoundaryService[schemas.Eldership, schemas.EldershipWithGeometry](
    model_class=models.Elderships,
    additional_select_columns=[
        models.Elderships.area_ha,
        _municipality_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Elderships, models.Elderships.municipality
    ).outerjoin(models.Municipalities.county),
)

residential_areas_service = BoundaryService[schemas.ResidentialArea, schemas.ResidentialAreaWithGeometry](
    model_class=models.ResidentialAreas,
    additional_select_columns=[
        models.ResidentialAreas.area_ha,
        _municipality_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.ResidentialAreas, models.ResidentialAreas.municipality
    ).outerjoin(models.Municipalities.county),
)

streets_service = BoundaryService[schemas.Street, schemas.StreetWithGeometry](
    model_class=models.Streets,
    additional_select_columns=[
        models.Streets.length_m,
        models.Streets.full_name,
        _residential_area_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Streets, models.Streets.residential_area
    ).outerjoin(models.ResidentialAreas.municipality).outerjoin(models.Municipalities.county),
)


class AddressesService:

    @staticmethod
    def _select_addresses(srid: int):
        query = (select(
            models.Addresses.feature_id,
            models.Addresses.code,
            models.Addresses.plot_or_building_number,
            models.Addresses.building_block_number,
            models.Addresses.postal_code,
            _flat_residential_area_object,
            _municipality_object,
            _flat_street_object,
            func.json_object(
                "longitude", ST_Y(ST_Transform(models.Addresses.geom, srid)),
                "latitude", ST_X(ST_Transform(models.Addresses.geom, srid)),
                type_=JSONB,
            ).label("location"),
        ).select_from(models.Addresses)
                 .outerjoin(models.Addresses.municipality)
                 .outerjoin(models.Municipalities.county)
                 .outerjoin(models.Addresses.street)
                 .outerjoin(models.Addresses.residential_area)
                 .order_by(models.Addresses.code.asc()))

        return query

    @staticmethod
    def search(
            db: Session,
            sort_by: schemas.SearchSortBy,
            sort_order: schemas.SearchSortOrder,
            geometry_filter: Optional[schemas.GeometryFilter],
            name_filter: Optional[schemas.NameFilter],
            codes: Optional[List[str]],
            feature_ids: Optional[List[int]],
            srid: int,
    ):
        query = AddressesService._select_addresses(srid=srid)
        return paginate(db, query, unique=False)

    @staticmethod
    def get(
            db: Session,
            code: int,
            srid: int,
    ) -> Row | None:
        query = AddressesService._select_addresses(srid=srid)
        query = query.filter(models.Addresses.code == code)

        return db.execute(query).first()
