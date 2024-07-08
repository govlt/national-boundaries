from abc import ABC

from geoalchemy2.functions import ST_Intersects, ST_Transform, ST_GeomFromEWKT, ST_Contains, ST_IsValid
from sqlalchemy import Select
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql.functions import GenericFunction, func
from sqlean import OperationalError

import database
import models
import schemas


class BaseFilter(ABC):
    def apply(
            self,
            request: schemas.BaseSearchRequest,
            db: Session,
            query: Select,
    ):
        if geometry_filter := request.geometry:
            query = self._apply_geometry_filter(
                geometry_filter=geometry_filter,
                db=db,
                query=query
            )
        return query

    def _apply_general_boundaries_filter(
            self,
            general_boundaries_filter: schemas.GeneralBoundariesFilter,
            query: Select,
            model_class: type[models.BaseBoundaries],
    ) -> Select:
        if hasattr(model_class, 'name') and general_boundaries_filter.name:
            query = _filter_by_string_field(
                string_filter=general_boundaries_filter.name,
                query=query,
                string_field=getattr(model_class, 'name')
            )

        feature_ids = general_boundaries_filter.feature_ids
        if feature_ids and len(general_boundaries_filter.feature_ids) > 0:
            query = query.filter(getattr(model_class, 'feature_id').in_(feature_ids))

        codes = general_boundaries_filter.codes
        if codes and len(codes) > 0:
            query = query.filter(getattr(model_class, 'code').in_(codes))

        return query

    def _apply_geometry_filter(
            self,
            geometry_filter: schemas.GeometryFilter,
            db: Session,
            query: Select,
    ) -> Select:
        filter_func_type = _get_filter_func(geometry_filter.method)
        geom_field = self.Meta.geom_field
        if geom_field is None:
            raise ValueError('geom_field in meta is not defined')

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


class CountiesFilter(BaseFilter):
    def apply(
            self,
            request: schemas.CountiesSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)

        if counties_filter := request.counties:
            query = self._apply_general_boundaries_filter(
                general_boundaries_filter=counties_filter,
                query=query,
                model_class=models.Counties
            )

        return query

    class Meta:
        geom_field = models.Counties.geom


class MunicipalitiesFilter(CountiesFilter):

    def apply(
            self,
            request: schemas.MunicipalitiesSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if municipalities_filter := request.municipalities:
            query = self._apply_general_boundaries_filter(
                general_boundaries_filter=municipalities_filter,
                query=query,
                model_class=models.Municipalities
            )

        return query

    class Meta:
        geom_field = models.Municipalities.geom


class EldershipsFilter(MunicipalitiesFilter):

    def apply(
            self,
            request: schemas.EldershipsSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if elderships_filter := request.elderships:
            query = self._apply_general_boundaries_filter(
                general_boundaries_filter=elderships_filter,
                query=query,
                model_class=models.Elderships
            )
        return query

    class Meta:
        geom_field = models.Elderships.geom


class ResidentialAreasFilter(MunicipalitiesFilter):
    def apply(
            self,
            request: schemas.ResidentialAreasSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if residential_areas_filter := request.residential_areas:
            query = self._apply_general_boundaries_filter(
                general_boundaries_filter=residential_areas_filter,
                query=query,
                model_class=models.ResidentialAreas
            )

        return query

    class Meta:
        geom_field = models.ResidentialAreas.geom


class StreetsFilter(ResidentialAreasFilter):
    def apply(
            self,
            request: schemas.StreetsSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)
        if streets_filter := request.streets:
            query = self._apply_general_boundaries_filter(
                general_boundaries_filter=streets_filter,
                query=query,
                model_class=models.Streets
            )

            if streets_filter.full_name:
                query = _filter_by_string_field(
                    string_filter=streets_filter.full_name,
                    query=query,
                    string_field=models.Streets.full_name
                )

        return query

    class Meta:
        geom_field = models.Streets.geom


class AddressesFilter(StreetsFilter):

    def apply(
            self,
            request: schemas.AddressesSearchRequest,
            db: Session,
            query: Select,
    ) -> Select:
        address_query = super().apply(request, db, query)
        if address_filter := request.addresses:
            address_query = self._apply_streets_filters(address_filter, address_query)

        return address_query

    @staticmethod
    def _apply_streets_filters(
            address_filter: schemas.AddressesFilter,
            query: Select,
    ) -> Select:
        address_query = query

        if address_filter.building_block_number:
            address_query = _filter_by_string_field(
                string_filter=address_filter.building_block_number,
                query=address_query,
                string_field=models.Addresses.building_block_number
            )
        if address_filter.plot_or_building_number:
            address_query = _filter_by_string_field(
                string_filter=address_filter.plot_or_building_number,
                query=address_query,
                string_field=models.Addresses.plot_or_building_number
            )
        if address_filter.postal_code:
            address_query = _filter_by_string_field(
                string_filter=address_filter.postal_code,
                query=address_query,
                string_field=models.Addresses.postal_code
            )

        feature_ids = address_filter.feature_ids
        if feature_ids and len(address_filter.feature_ids) > 0:
            address_query = address_query.filter(models.Addresses.feature_id.in_(feature_ids))

        codes = address_filter.codes
        if codes and len(codes) > 0:
            address_query = address_query.filter(models.Addresses.code.in_(codes))

        return address_query

    class Meta:
        geom_field = models.Addresses.geom


class RoomsFilter(StreetsFilter):

    def apply(
            self,
            request: schemas.RoomsSearchRequest,
            db: Session,
            query: Select,
    ):
        query = super().apply(request, db, query)

        if room_filter := request.rooms:
            query = self._apply_rooms_filters(room_filter, query)

        return query

    @staticmethod
    def _apply_rooms_filters(
            rooms_filter: schemas.RoomsFilter,
            query: Select,
    ) -> Select:
        rooms_query = query

        if rooms_filter.room_number:
            rooms_query = _filter_by_string_field(
                string_filter=rooms_filter.room_number,
                query=rooms_query,
                string_field=models.Rooms.room_number
            )
        codes = rooms_filter.codes
        if codes and len(codes) > 0:
            rooms_query = rooms_query.filter(models.Rooms.code.in_(codes))

        return rooms_query

    class Meta:
        geom_field = models.Addresses.geom


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
        filter_func_type: type[GenericFunction],
        geom_from_func_type: type[GenericFunction],
):
    geom = ST_Transform(geom_from_func_type(geom_value), 3346)
    if not _is_valid_geometry(db, geom):
        raise InvalidFilterGeometry(message="Invalid geometry", field=field, value=geom_value)

    return query.where(filter_func_type(geom, geom_field))


def _get_filter_func(filter_method: schemas.GeometryFilterMethod) -> type[GenericFunction]:
    match filter_method:
        case schemas.GeometryFilterMethod.intersects:
            return ST_Intersects
        case schemas.GeometryFilterMethod.contains:
            return ST_Contains
        case _:
            raise ValueError(f"Unknown geometry filter method: {filter_method}")


def _filter_by_string_field(
        string_filter: schemas.StringFilter,
        query: Select,
        string_field: InstrumentedAttribute
) -> Select:
    if string_filter.exact:
        query = query.filter(func.lower(string_field) == string_filter.exact.lower())
    elif string_filter.starts:
        query = query.filter(string_field.istartswith(string_filter.starts))
    elif string_filter.contains:
        query = query.filter(string_field.icontains(string_filter.contains))

    return query


class InvalidFilterGeometry(Exception):
    def __init__(self, message: str, field: str, value: str):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
