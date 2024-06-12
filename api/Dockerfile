# Stage 1: Prepare SQLite database
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.9.0 as database-builder
WORKDIR /opt/database

# Counties
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json counties.json
RUN ogr2ogr -f SQLite boundaries.sqlite counties.json -dsco SPATIALITE=YES -lco FID=id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS id, APS_KODAS AS code, APS_PAV as name, APS_PLOTAS as area_ha FROM counties"

# Municipalities
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json municipalities.json
RUN ogr2ogr -append -f SQLite boundaries.sqlite municipalities.json -lco FID=id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS id, SAV_KODAS AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, APS_KODAS as county_code FROM municipalities"

# Elderships
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json elderships.json
RUN ogr2ogr -append -f SQLite boundaries.sqlite elderships.json -lco FID=id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS id, SEN_KODAS AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM elderships"

# Residential areas
ADD https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json residential_areas.json
RUN ogr2ogr -append -f SQLite boundaries.sqlite residential_areas.json -lco FID=id -lco GEOMETRY_NAME=geom -sql "SELECT FID AS id, GYV_KODAS AS code, GYV_PAV as name, PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM residential_areas"

# Stage 2: Base image
FROM node:20-alpine as base

# Required for dependencies coming from git
RUN apk add --no-cache git

# Stage 3: Builder image
FROM base as builder

# Set the working directory
WORKDIR /app

# Install dependencies
COPY package.json yarn.lock ./
RUN yarn install --immutable --immutable-cache --inline-builds --production=false

# Copy source
COPY . .

# Build the application
RUN yarn build

# Stage 4: Final production image
FROM base

# Set the working directory
WORKDIR /app

# Install only production dependencies
COPY package.json yarn.lock ./
RUN yarn install --immutable --immutable-cache --inline-builds --production \
    && yarn cache clean

# Copy built artifacts from builder stage
COPY --from=builder /app/dist/ ./dist/
COPY --from=database-builder --chmod=444 /opt/database/boundaries.sqlite ./

# Docker build args and environment variables
ARG VERSION
ENV VERSION=${VERSION}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}

# Set default environment variables
ENV NODE_ENV=production
ENV TZ=Etc/GMT

# Expose application port
EXPOSE 3000

# Start the server
CMD ["sh", "-c", "yarn start"]