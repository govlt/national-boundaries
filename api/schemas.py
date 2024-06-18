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


class BoundariesSearchRequest(BaseModel):
    srid: Optional[int] = Field(
        default=3346,
        examples=[4326],
        description="Spatial reference identifier used for geometry filtering (default is 3346). "
                    "For instance 3346 is LKS, 4326 is for World Geodetic System 1984 (WGS 84)",
    )

    wkt: Optional[str] = Field(
        default=None,
        description="Well-Known Text (WKT) for geometry filtering by intersect",
        examples=[
            "POLYGON ((25.277429 54.687233, 25.277429 54.680658, 25.289244 54.680658, 25.289244 54.687233, "
            "25.277429 54.687233))"
        ],
    )

    codes: Optional[List[str]] = Field(
        default=None,
        description="Filter by codes",
        examples=[
            None
        ],
    )

    feature_ids: Optional[List[int]] = Field(
        default=None,
        description="Filter by feature IDs",
        examples=[
            None
        ],
    )

    name_contains: Optional[str] = Field(
        default=None,
        description="Filter by name containing a string (case insensitive)",
        examples=[
            None
        ],
    )

    name_start: Optional[str] = Field(
        default=None,
        description="Filter by name starting with a string (case insensitive)",
        examples=[
            None
        ],
    )
