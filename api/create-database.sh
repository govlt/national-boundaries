#!/bin/bash

set -e

# Function to calculate MD5 checksum
calculate_md5() {
    local file="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        md5 -r "$file"
    else
        # Linux and other Unix-like systems
        md5sum "$file"
    fi
}

echo "Starting data processing"

rm -rf boundaries.sqlite data-sources

mkdir -p data-sources

echo "Importing counties data into SQLite"
curl -f -o data-sources/counties.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json
calculate_md5 data-sources/counties.json >> data-sources/checksums.txt
ogr2ogr -f SQLite boundaries.sqlite data-sources/counties.json -dsco SPATIALITE=YES -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, APS_KODAS AS code, APS_PAV as name, APS_PLOTAS as area_ha FROM counties"
ogrinfo -sql "CREATE UNIQUE INDEX counties_code ON counties(code)" boundaries.sqlite

echo "Importing municipalities data into SQLite"
curl -f -o data-sources/municipalities.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json
calculate_md5 data-sources/municipalities.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/municipalities.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, SAV_KODAS AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, APS_KODAS as county_code FROM municipalities"
ogrinfo -sql "CREATE UNIQUE INDEX municipalities_code ON municipalities(code)" boundaries.sqlite

echo "Importing elderships data into SQLite"
curl -f -o data-sources/elderships.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json
calculate_md5 data-sources/elderships.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/elderships.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, SEN_KODAS AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM elderships"
ogrinfo -sql "CREATE UNIQUE INDEX elderships_code ON elderships(code)" boundaries.sqlite

echo "Importing residential areas data into SQLite"
curl -f -o data-sources/residential_areas.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json
calculate_md5 data-sources/residential_areas.json >> data-sources/checksums.txt
# For some reason GYV_KODAS is numeric in RC specification, convert it to text
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/residential_areas.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(GYV_KODAS AS character(255)) AS code, GYV_PAV as name, PLOTAS as area_ha, SAV_KODAS AS municipality_code FROM residential_areas"
ogrinfo -sql "CREATE UNIQUE INDEX residential_areas_code ON residential_areas(code)" boundaries.sqlite

echo "Finalizing SQLite database"
ogrinfo boundaries.sqlite -sql "VACUUM"

echo "SQLite database created successfully"
