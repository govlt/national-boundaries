import os

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

import models
import router
import schemas
import service
from database import engine

if SENTRY_DSN := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = FastAPI(
    title="National Boundaries API",
    summary="Provides data about the national boundaries of Lithuania",
    version="0.0.1",
    terms_of_service="https://www.registrucentras.lt/p/1187",
    docs_url="/",
    contact={
        "name": "Karolis Vyčius",
        "url": "https://vycius.lt/",
        "email": "karolis@vycius.lt",
    },
    license_info={
        "name": "CC BY 4.0",
        "url": "https://github.com/govlt/national-boundaries",
        "identifier": "CC-BY-4.0",
    },
)

models.Base.metadata.create_all(bind=engine)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.county_service,
        response_model=schemas.County,
        response_with_geometry_model=schemas.CountyWithGeometry,
        item_name="county",
        item_name_plural="counties",
        example_code="10"
    ),
    prefix="/v1/counties",
    tags=["counties"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.municipalities_service,
        response_model=schemas.Municipality,
        response_with_geometry_model=schemas.MunicipalityWithGeometry,
        item_name="municipality",
        item_name_plural="municipalities",
        example_code="13",
    ),
    prefix="/v1/municipalities",
    tags=["municipalities"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.elderships_service,
        response_model=schemas.Eldership,
        response_with_geometry_model=schemas.EldershipWithGeometry,
        item_name="eldership",
        item_name_plural="elderships",
        example_code="1306",
    ),
    prefix="/v1/elderships",
    tags=["elderships"],
)

app.include_router(
    router.create_boundaries_router(
        boundary_service=service.residential_areas_service,
        response_model=schemas.ResidentialArea,
        response_with_geometry_model=schemas.ResidentialAreaWithGeometry,
        item_name="residential area",
        item_name_plural="residential areas",
        example_code="31003"
    ),
    prefix="/v1/residential-areas",
    tags=["residential-areas"],
)

app.include_router(router.health_check_router)

add_pagination(app)


def main() -> None:
    uvicorn.run("main:app", host="0.0.0.0", server_header=False)


if __name__ == "__main__":
    main()
