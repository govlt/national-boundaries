from typing import Optional, List, Callable, Type

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from geoalchemy2.functions import ST_Intersects, ST_Transform, ST_GeomFromText
from sqlalchemy import select, Select, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, InstrumentedAttribute

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
            model_class.area_ha,
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

    def search(
            self,
            db: Session,
            sort_by: schemas.SearchSortBy,
            sort_order: schemas.SearchSortOrder,
            wkt: Optional[str],
            srid: int,
            codes: Optional[List[str]],
            feature_ids: Optional[List[int]],
            name_contains=Optional[str],
            name_start=Optional[str]
    ) -> Page[Type[S]]:
        query = self.select_func(self.base_columns)
        if wkt:
            query = query.where(
                ST_Intersects(
                    self.model_class.geom,
                    ST_Transform(ST_GeomFromText(wkt, srid), 3346)
                )
            )

        if feature_ids and len(feature_ids) > 0:
            query = query.filter(self.model_class.feature_id.in_(feature_ids))

        if codes and len(codes) > 0:
            query = query.filter(self.model_class.code.in_(codes))

        if name_contains:
            query = query.filter(self.model_class.name.icontains(name_contains))

        if name_start:
            query = query.filter(self.model_class.name.istartswith(name_start))

        sort_by_field = getattr(self.model_class, sort_by)

        if sort_order == schemas.SearchSortOrder.desc:
            sort_by_field = sort_by_field.desc()

        query = query.order_by(sort_by_field)

        return paginate(db, query, unique=False)


county_service = BoundaryService[schemas.County, schemas.CountyWithGeometry](
    model_class=models.Counties,
    additional_select_columns=[],
    select_func=lambda columns: select(*columns).select_from(models.Counties),
)

municipalities_service = BoundaryService[schemas.Municipality, schemas.MunicipalityWithGeometry](
    model_class=models.Municipalities,
    additional_select_columns=[
        _county_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Municipalities, models.Municipalities.county
    ),
)

elderships_service = BoundaryService[schemas.Eldership, schemas.EldershipWithGeometry](
    model_class=models.Elderships,
    additional_select_columns=[
        _municipality_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Elderships, models.Elderships.municipality
    ).outerjoin(models.Municipalities.county),
)

residential_areas_service = BoundaryService[schemas.ResidentialArea, schemas.ResidentialAreaWithGeometry](
    model_class=models.ResidentialAreas,
    additional_select_columns=[
        _municipality_object,
    ],
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.ResidentialAreas, models.ResidentialAreas.municipality
    ).outerjoin(models.Municipalities.county),
)
