from typing import Optional, List, Callable, Type

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from geoalchemy2.functions import ST_Transform, ST_X, ST_Y
from sqlalchemy import select, Select, func, text, Row
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql import operators

import filters
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

    def _filter_by_name(self, query: Select, name_filter: schemas.StringFilter) -> Select:
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
            request: schemas.BaseSearchRequest,
            base_filter: filters.BaseFilter,
    ) -> Page[Type[S]]:
        query = self.select_func(self.base_columns)

        query = base_filter.apply(request=request, db=db, query=query)

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
            request: schemas.AddressesSearchRequest,
            addresses_filter: filters.AddressesFilter,
            srid: int,
    ):
        query = AddressesService._select_addresses(srid=srid)

        query = addresses_filter.apply(request, db, query)

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
