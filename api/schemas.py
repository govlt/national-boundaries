from pydantic import BaseModel


class Geometry(BaseModel):
    srid: int
    data: str


class County(BaseModel):
    code: str
    name: str
    area_ha: float

    class Config:
        from_attributes = True


class CountyWithGeometry(County):
    geometry: Geometry


class Municipality(BaseModel):
    code: str
    name: str
    area_ha: float

    county: County

    class Config:
        from_attributes = True


class MunicipalityWithGeometry(Municipality):
    geometry: Geometry


class Eldership(BaseModel):
    code: str
    name: str
    area_ha: float

    municipality: Municipality

    class Config:
        from_attributes = True


class EldershipWithGeometry(Eldership):
    geometry: Geometry


class ResidentialArea(BaseModel):
    code: str
    name: str
    area_ha: float

    municipality: Municipality

    class Config:
        from_attributes = True


class ResidentialAreaWithGeometry(Eldership):
    geometry: Geometry


class HTTPExceptionResponse(BaseModel):
    detail: str
