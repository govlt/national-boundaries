# Stage 1: Prepare SQLite database
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.9.0 as database-builder
WORKDIR /opt/database

# Counties
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json counties.json
RUN ogr2ogr -f SQLite boundaries.sqlite counties.json -dsco SPATIALITE=YES -lco FID=feature_id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS feature_id, APS_KODAS AS code, APS_PAV as name, APS_PLOTAS as area_ha FROM counties"
RUN ogrinfo -sql "CREATE UNIQUE INDEX counties_code ON counties(code)" boundaries.sqlite

# Municipalities
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json municipalities.json
RUN ogr2ogr -append -f SQLite boundaries.sqlite municipalities.json -lco FID=feature_id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS feature_id, SAV_KODAS AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, APS_KODAS as county_code FROM municipalities"
RUN ogrinfo -sql "CREATE UNIQUE INDEX municipalities_code ON municipalities(code)" boundaries.sqlite

# Elderships
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json elderships.json
RUN ogr2ogr -append -f SQLite boundaries.sqlite elderships.json -lco FID=feature_id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS feature_id, SEN_KODAS AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM elderships"
RUN ogrinfo -sql "CREATE UNIQUE INDEX elderships_code ON elderships(code)" boundaries.sqlite

# Residential areas
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json residential_areas.json
# For some reason GYV_KODAS is numeric in RC specification, convert it to text
RUN ogr2ogr -append -f SQLite boundaries.sqlite residential_areas.json -lco FID=feature_id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS feature_id, CAST(GYV_KODAS AS character(255)) AS code, GYV_PAV as name, PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM residential_areas"
RUN ogrinfo -sql "CREATE UNIQUE INDEX residential_areas_code ON residential_areas(code)" boundaries.sqlite


# Multi stage poetry docker build https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
FROM python:3.12 as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim

WORKDIR /opt/app

# Required for using SpatialLite
RUN apt-get update && apt-get install -y \
  spatialite-bin \
  libsqlite3-mod-spatialite \
  && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    SPATIALITE_LIBRARY_PATH=mod_spatialite.so \
    SENTRY_DSN="" \
    SENTRY_ENVIRONMENT="production"


COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

COPY --from=database-builder --chmod=444 /opt/database/boundaries.sqlite ./

CMD ["fastapi", "run", "main.py", "--port", "80"]
