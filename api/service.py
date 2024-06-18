from typing import Optional, List, Callable, Type

from fastapi_filter.contrib.sqlalchemy import Filter
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


class BoundaryService[M, S, G]:
    model_class: type(models.Base)
    base_columns: List[InstrumentedAttribute]
    code_column: InstrumentedAttribute
    geometry_column: InstrumentedAttribute
    select_func: Callable[[List[InstrumentedAttribute]], Select]

    def __init__(
            self,
            model_class: type(models.Base),
            base_columns: List[InstrumentedAttribute],
            code_column: InstrumentedAttribute,
            geometry_column: InstrumentedAttribute,
            select_func: Callable[[List[InstrumentedAttribute]], Select],
    ):
        self.model_class = model_class
        self.base_columns = base_columns
        self.code_column = code_column
        self.geometry_column = geometry_column
        self.select_func = select_func

    def get_without_geometry(self, db: Session, code: str) -> Optional[Type[S]]:
        query = self.select_func(self.base_columns)
        query = query.filter(self.code_column == code)

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
                ST_Transform(self.geometry_column, srid).label("geometry"),
            ]
        )
        query = query.filter(self.code_column == code)

        return db.execute(query).first()

    def search(
            self,
            db: Session,
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
                    self.geometry_column,
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

        return paginate(db, query, unique=False)


county_service = BoundaryService[models.Counties, schemas.County, schemas.CountyWithGeometry](
    model_class=models.Counties,
    base_columns=[
        models.Counties.name,
        models.Counties.code,
        models.Counties.feature_id,
        models.Counties.area_ha,
    ],
    code_column=models.Counties.code,
    geometry_column=models.Counties.geom,
    select_func=lambda columns: select(*columns).select_from(models.Counties),
)

municipalities_service = BoundaryService[
    models.Municipalities, schemas.Municipality, schemas.MunicipalityWithGeometry
](
    model_class=models.Municipalities,
    base_columns=[
        models.Municipalities.name,
        models.Municipalities.code,
        models.Municipalities.feature_id,
        models.Municipalities.area_ha,
        _county_object,
    ],
    code_column=models.Municipalities.code,
    geometry_column=models.Municipalities.geom,
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Municipalities, models.Municipalities.county
    ),
)

elderships_service = BoundaryService[
    models.Elderships, schemas.Eldership, schemas.EldershipWithGeometry
](
    model_class=models.Elderships,
    base_columns=[
        models.Elderships.name,
        models.Elderships.code,
        models.Elderships.feature_id,
        models.Elderships.area_ha,
        _municipality_object,
    ],
    code_column=models.Elderships.code,
    geometry_column=models.Elderships.geom,
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.Elderships, models.Elderships.municipality
    ).outerjoin(models.Municipalities.county),
)

residential_areas_service = BoundaryService[
    models.ResidentialAreas, schemas.ResidentialArea, schemas.ResidentialAreaWithGeometry
](
    model_class=models.ResidentialAreas,
    base_columns=[
        models.ResidentialAreas.name,
        models.ResidentialAreas.code,
        models.ResidentialAreas.feature_id,
        models.ResidentialAreas.area_ha,
        _municipality_object,
    ],
    code_column=models.ResidentialAreas.code,
    geometry_column=models.ResidentialAreas.geom,
    select_func=lambda columns: select(*columns).outerjoin_from(
        models.ResidentialAreas, models.ResidentialAreas.municipality
    ).outerjoin(models.Municipalities.county),
)
