import enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SearchSortBy(enum.StrEnum):
    code = 'code'
    name = 'name'
    feature_id = 'feature_id'
    area_ha = 'area_ha'


class SearchSortOrder(str, enum.Enum):
    asc = 'asc'
    desc = 'desc'


class Geometry(BaseModel):
    srid: int = Field(description="Spatial Reference Identifier (SRID) for the geometry")
    data: str = Field(description="Geometry data in WKB (Well-Known Binary) format, represented as a hex string")


class County(BaseModel):
    code: str = Field(description="Unique code of the county")
    name: str = Field(description="Name of the county")
    feature_id: int = Field(description="Feature ID of the county")
    area_ha: float = Field(description="Area of the county in hectares")

    class Config:
        from_attributes = True


class CountyWithGeometry(County):
    geometry: Geometry = Field(description="Geometry information of the county")


class Municipality(BaseModel):
    code: str = Field(description="Unique code of the municipality")
    name: str = Field(description="Name of the municipality")
    feature_id: int = Field(description="Feature ID of the municipality")
    area_ha: float = Field(description="Area of the municipality in hectares")
    county: County = Field(description="County information the municipality belongs to")

    class Config:
        from_attributes = True


class MunicipalityWithGeometry(Municipality):
    geometry: Geometry = Field(description="Geometry information of the municipality")


class Eldership(BaseModel):
    code: str = Field(description="Unique code of the eldership")
    name: str = Field(description="Name of the eldership")
    feature_id: int = Field(description="Feature ID of the eldership")
    area_ha: float = Field(description="Area of the eldership in hectares")
    municipality: Municipality = Field(description="Municipality information the eldership belongs to")

    class Config:
        from_attributes = True


class EldershipWithGeometry(Eldership):
    geometry: Geometry = Field(description="Geometry information of the eldership")


class ResidentialArea(BaseModel):
    code: str = Field(description="Unique code of the residential area")
    name: str = Field(description="Name of the residential area")
    feature_id: int = Field(description="Feature ID of the residential area")
    area_ha: float = Field(description="Area of the residential area in hectares")
    municipality: Municipality = Field(description="Municipality information the residential area belongs to")

    class Config:
        from_attributes = True


class ResidentialAreaWithGeometry(Eldership):
    geometry: Geometry = Field(description="Geometry information of the residential area")


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    healthy: bool = Field(description="Health status of the service")


class HTTPExceptionResponse(BaseModel):
    detail: str = Field(description="Detailed error message")

    class Config:
        json_schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


class NameFilter(BaseModel):
    contains: Optional[str] = Field(
        default=None,
        description="Filter by name containing a string (case insensitive)",
        examples=[
            "vil"
        ],
    )

    starts: Optional[str] = Field(
        default=None,
        description="Filter by name starting with a string (case insensitive)",
        examples=[
            "Vil"
        ],
    )


class GeometryFilterMethod(enum.StrEnum):
    intersects = 'intersects'
    contains = 'contains'


class GeometryFilter(BaseModel):
    method: GeometryFilterMethod = Field(
        default=GeometryFilterMethod.intersects,
        description="Defines method used for filtering geometries:\n"
                    "- **`intersects`**: filter geometries that intersects any portion of space with the specified "
                    "geometry.\n"
                    "- **`contains`**: filter geometries that are completely within the specified geometry."
    )
    ewkb: Optional[str] = Field(
        default=None,
        description="Extended Well-Known Binary (EWKB) represented as a hex string for geometry filtering",
        examples=[
            r"0103000020E6100000010000000500000045F6419605473940B1DD3D40F7574B4045F641960547394061E124CD1F57"
            r"4B40719010E50B4A394061E124CD1F574B40719010E50B4A3940B1DD3D40F7574B4045F6419605473940B1DD3D40F7574B40"
        ],
    )

    ewkt: Optional[str] = Field(
        default=None,
        description="Extended Well-Known Text (EWKT) for geometry filtering",
        examples=[
            "SRID=4326;POLYGON((25.277429 54.687233, 25.277429 54.680658, 25.289244 54.680658, 25.289244 54.687233, "
            "25.277429 54.687233))"
        ],
    )

    geojson: Optional[str] = Field(
        default=None,
        description="GeoJson for geometry filtering",
        examples=[
            r'{"crs":{"type":"name","properties":{"name":"EPSG:4326"}},"type":"Polygon","coordinates":[[[25.277429,'
            r'54.687233],[25.277429,54.680658],[25.289244,54.680658],[25.289244,54.687233],[25.277429,54.687233]]]}'
        ],
    )


class BoundariesSearchRequest(BaseModel):
    codes: Optional[List[str]] = Field(
        default=None,
        description="Filter by codes",
        examples=[
            []
        ],
    )

    feature_ids: Optional[List[int]] = Field(
        default=None,
        description="Filter by feature IDs",
        examples=[
            []
        ],
    )

    name: Optional[NameFilter] = Field(
        default=None,
        description="Filter by name"
    )

    geometry: Optional[GeometryFilter] = Field(
        default=None,
        description="Filter by geometry",
    )
