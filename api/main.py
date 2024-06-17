import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette import status

import filters
import models
import router
import schemas
import service
from database import engine

app = FastAPI(
    title="National boundaries API",
    summary="API: National Boundaries of Lithuania",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    docs_url="/",
    contact={
        "name": "Karolis Vyčius",
        "url": "https://vycius.lt/",
        "email": "karolis@vycius.lt",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/govlt/national-boundaries",
        "identifier": "MIT",
    },
)

models.Base.metadata.create_all(bind=engine)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.county_service,
        query_filter=filters.CountiesFilter,
        response_model=schemas.County,
        response_with_geometry_model=schemas.CountyWithGeometry,
        item_name="county",
        item_name_plural="counties"
    ),
    prefix="/counties",
    tags=["counties"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.municipalities_service,
        query_filter=filters.MunicipalityFilter,
        response_model=schemas.Municipality,
        response_with_geometry_model=schemas.MunicipalityWithGeometry,
        item_name="municipality",
        item_name_plural="municipalities"

    ),
    prefix="/municipalities",
    tags=["municipalities"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.elderships_service,
        query_filter=filters.EldershipsFilter,
        response_model=schemas.Eldership,
        response_with_geometry_model=schemas.EldershipWithGeometry,
        item_name="eldership",
        item_name_plural="elderships"

    ),
    prefix="/elderships",
    tags=["elderships"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.residential_areas_service,
        query_filter=filters.ResidentialAreasFilter,
        response_model=schemas.ResidentialArea,
        response_with_geometry_model=schemas.ResidentialAreaWithGeometry,
        item_name="residential area",
        item_name_plural="residential areas"

    ),
    prefix="/residential-areas",
    tags=["residential-areas"],
)

app.include_router(router.health_check_router)

add_pagination(app)


def main() -> None:
    uvicorn.run("main:app", host="0.0.0.0", server_header=False)


if __name__ == "__main__":
    main()
