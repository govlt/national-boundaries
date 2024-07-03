from geoalchemy2.functions import ST_Intersects, ST_Transform, ST_GeomFromEWKT, ST_Contains, ST_IsValid
from sqlalchemy import Select
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql.functions import GenericFunction
from sqlean import OperationalError

import database
import models
import schemas


class BaseFilter:
    def apply(
            self,
            request: schemas.BaseSearchRequest,
            db: Session,
            query: Select,
    ):
        pass


class CountiesFilter(BaseFilter):
    def apply(
            self,
            request: schemas.CountiesSearchRequest,
            db: Session,
            query: Select,
    ):
        if counties_filter := request.counties:
            query = _apply_general_boundaries_filter(
                general_boundaries_filter=counties_filter,
                query=query,
                db=db,
                name_field=models.Counties.name,
                feature_id_field=models.Counties.feature_id,
                code_field=models.Counties.code,
                geometry_field=models.Counties.geom,
            )

        return query


class MunicipalitiesFilter(CountiesFilter):
    def apply(
            self,
            request: schemas.MunicipalitiesSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if municipalities_filter := request.municipalities:
            query = _apply_general_boundaries_filter(
                general_boundaries_filter=municipalities_filter,
                query=query,
                db=db,
                name_field=models.Municipalities.name,
                feature_id_field=models.Municipalities.feature_id,
                code_field=models.Municipalities.code,
                geometry_field=models.Municipalities.geom,
            )

        return query


class EldershipsFilter(MunicipalitiesFilter):
    def apply(
            self,
            request: schemas.EldershipsSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if elderships_filter := request.elderships:
            query = _apply_general_boundaries_filter(
                general_boundaries_filter=elderships_filter,
                query=query,
                db=db,
                name_field=models.Elderships.name,
                feature_id_field=models.Elderships.feature_id,
                code_field=models.Elderships.code,
                geometry_field=models.Elderships.geom,
            )
        return query


class ResidentialAreasFilter(MunicipalitiesFilter):
    def apply(
            self,
            request: schemas.ResidentialAreasSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if residential_areas_filter := request.residential_areas:
            query = _apply_general_boundaries_filter(
                general_boundaries_filter=residential_areas_filter,
                query=query,
                db=db,
                name_field=models.ResidentialAreas.name,
                feature_id_field=models.ResidentialAreas.feature_id,
                code_field=models.ResidentialAreas.code,
                geometry_field=models.ResidentialAreas.geom,
            )

        return query


class StreetsFilter(ResidentialAreasFilter):
    def apply(
            self,
            request: schemas.StreetsSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if streets_filter := request.streets:
            query = _apply_general_boundaries_filter(
                general_boundaries_filter=streets_filter,
                query=query,
                db=db,
                name_field=models.Streets.name,
                feature_id_field=models.Streets.feature_id,
                code_field=models.Streets.code,
                geometry_field=models.Streets.geom,
            )

        return query


class AddressesFilter(StreetsFilter):
    def apply(
            self,
            request: schemas.AddressesSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if addresses_filter := request.addresses:
            feature_ids = addresses_filter.feature_ids
            if feature_ids and len(feature_ids) > 0:
                query = query.filter(models.Addresses.feature_id.in_(feature_ids))

            codes = addresses_filter.codes
            if codes and len(codes) > 0:
                query = query.filter(models.Addresses.code.in_(codes))

        return query


def _is_valid_geometry(db: Session, geom: GenericFunction) -> bool:
    try:
        return db.execute(ST_IsValid(geom)).scalar() == 1
    except OperationalError:
        return False


def _filter_by_geometry(
        db: Session,
        query: Select,
        geom_value: str,
        field: str,
        geom_field: InstrumentedAttribute,
        filter_func_type: type(GenericFunction),
        geom_from_func_type: type(GenericFunction),
):
    geom = ST_Transform(geom_from_func_type(geom_value), 3346)
    if not _is_valid_geometry(db, geom):
        raise InvalidFilterGeometry(message="Invalid geometry", field=field, value=geom_value)

    return query.where(filter_func_type(geom, geom_field))


def _get_filter_func(filter_method: schemas.GeometryFilterMethod) -> type(GenericFunction):
    match filter_method:
        case schemas.GeometryFilterMethod.intersects:
            return ST_Intersects
        case schemas.GeometryFilterMethod.contains:
            return ST_Contains
        case _:
            raise ValueError(f"Unknown geometry filter method: {filter_method}")


def apply_geometry_filter(
        geometry_filter: schemas.GeometryFilter,
        db: Session,
        query: Select,
        geom_field: InstrumentedAttribute
) -> Select:
    filter_func_type = _get_filter_func(geometry_filter.method)

    if ewkb := geometry_filter.ewkb:
        query = _filter_by_geometry(
            db=db,
            query=query,
            field="ewkb",
            geom_value=ewkb,
            filter_func_type=filter_func_type,
            geom_from_func_type=database.GeomFromEWKB,
            geom_field=geom_field,
        )

    if ewkt := geometry_filter.ewkt:
        query = _filter_by_geometry(
            db=db,
            query=query,
            field="ewkt",
            geom_value=ewkt,
            filter_func_type=filter_func_type,
            geom_from_func_type=ST_GeomFromEWKT,
            geom_field=geom_field,
        )

    if geojson := geometry_filter.geojson:
        query = _filter_by_geometry(
            db=db,
            query=query,
            field="geojson",
            geom_value=geojson,
            filter_func_type=filter_func_type,
            geom_from_func_type=database.GeomFromGeoJSON,
            geom_field=geom_field,
        )

    return query


def _filter_by_string_field(
        string_filter: schemas.StringFilter,
        query: Select,
        string_field: InstrumentedAttribute
) -> Select:
    if string_filter.contains:
        query = query.filter(string_field.icontains(string_filter.contains))
    if string_filter.starts:
        query = query.filter(string_field.istartswith(string_filter.starts))

    return query


def _apply_general_boundaries_filter(
        general_boundaries_filter: schemas.GeneralBoundariesFilter,
        query: Select,
        db: Session,
        name_field: InstrumentedAttribute,
        feature_id_field: InstrumentedAttribute,
        code_field: InstrumentedAttribute,
        geometry_field: InstrumentedAttribute,
) -> Select:
    if name_filter := general_boundaries_filter.name:
        query = _filter_by_string_field(string_filter=name_filter, query=query, string_field=name_field)

    feature_ids = general_boundaries_filter.feature_ids
    if feature_ids and len(general_boundaries_filter.feature_ids) > 0:
        query = query.filter(feature_id_field.in_(feature_ids))

    codes = general_boundaries_filter.codes
    if codes and len(codes) > 0:
        query = query.filter(code_field.in_(codes))

    if geometry_filter := general_boundaries_filter.geometry:
        query = apply_geometry_filter(geometry_filter=geometry_filter, db=db, query=query, geom_field=geometry_field)

    return query


class InvalidFilterGeometry(Exception):
    def __init__(self, message: str, field: str, value: str):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
