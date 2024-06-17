from fastapi import HTTPException, APIRouter, Depends
from fastapi.params import Query
from fastapi_filter import FilterDepends
from fastapi_filter.base.filter import BaseFilterModel
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

import database
import schemas
from service import BoundaryService

_srid_query = Query(
    3346,
    example=4326,
    description="A spatial reference identifier (SRID). "
                "For instance 3346 is LKS, 4326 is for World Geodetic System 1984 (WGS 84)",
)


def create_boundaries_router(
        boundary_service: BoundaryService,
        query_filter: type[BaseFilterModel],
        response_model: type[BaseModel],
        response_with_geometry_model: type[BaseModel],
        item_name: str,
        item_name_plural: str,
):
    router = APIRouter()

    @router.post("/search", response_model=Page[response_model], summary=f"Paginated list of {item_name_plural}")
    def boundaries_search(
            request: schemas.GeometryFilterRequest,
            db: Session = Depends(database.get_db),
            boundaries_filter: Filter = FilterDepends(query_filter),
            srid: int = _srid_query,
    ):
        return boundary_service.search(
            db=db, wkt=request.wkt, srid=srid, query_filter=boundaries_filter
        )

    @router.get(
        "/{code}",
        response_model=response_model,
        summary=item_name.capitalize(),
        responses={
            404: {"description": "Not found", "model": schemas.HTTPExceptionResponse},
        },
    )
    def boundary_item(
            code: str,
            db: Session = Depends(database.get_db),
    ):
        if item := boundary_service.get_without_geometry(db=db, code=code):
            return item
        else:
            raise HTTPException(
                status_code=404,
                detail="Not found",
            )

    @router.get(
        "/{code}/geometry",
        response_model=response_with_geometry_model,
        summary=f"{item_name.capitalize()} with geometry",
        responses={
            404: {"description": "Not found", "model": schemas.HTTPExceptionResponse},
        },
    )
    def boundary_with_geometry(
            code: str,
            db: Session = Depends(database.get_db),
            srid: int = _srid_query,
    ):
        if row := boundary_service.get_with_geometry(db=db, code=code, srid=srid):
            return row
        else:
            raise HTTPException(
                status_code=404,
                detail="Not found",
            )

    return router


health_check_router = APIRouter()


# Healthcheck code is adapted from https://gist.github.com/Jarmos-san/0b655a3f75b698833188922b714562e5
@health_check_router.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=schemas.HealthCheck,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": schemas.HTTPExceptionResponse}}
)
def get_health(db: Session = Depends(database.get_db)) -> schemas.HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    try:
        result = db.execute(text("SELECT spatialite_version()"))
        spatialite_version = result.scalar()
        if spatialite_version:
            return schemas.HealthCheck(healthy=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not healthy"
            )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Not healthy"
        )
