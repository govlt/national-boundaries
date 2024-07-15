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
curl -f -L --max-redirs 5 --retry 3 -o data-sources/counties.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json
calculate_md5 data-sources/counties.json >> data-sources/checksums.txt
ogr2ogr -f SQLite boundaries.sqlite data-sources/counties.json -dsco SPATIALITE=YES -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(APS_KODAS AS integer(8)) AS code, APS_PAV as name, APS_PLOTAS as area_ha, APS_R AS created_at FROM counties"
ogrinfo -sql "CREATE UNIQUE INDEX counties_code ON counties(code)" boundaries.sqlite

echo "Importing municipalities data into SQLite"
curl -f -L --max-redirs 5 --retry 3 -o data-sources/municipalities.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json
calculate_md5 data-sources/municipalities.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/municipalities.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(SAV_KODAS AS integer(8)) AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, CAST(APS_KODAS AS integer(8)) as county_code, SAV_R AS created_at FROM municipalities"
ogrinfo -sql "CREATE UNIQUE INDEX municipalities_code ON municipalities(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX municipalities_county_code ON municipalities(county_code)" boundaries.sqlite

echo "Importing elderships data into SQLite"
curl -f -L --max-redirs 5 --retry 3 -o data-sources/elderships.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json
calculate_md5 data-sources/elderships.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/elderships.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(SEN_KODAS AS integer(8)) AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, SEN_R AS created_at FROM elderships"
ogrinfo -sql "CREATE UNIQUE INDEX elderships_code ON elderships(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX elderships_municipality_code_and_name ON elderships(municipality_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing residential areas data into SQLite"
curl -f -L --max-redirs 5 --retry 3 -o data-sources/residential_areas.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json
calculate_md5 data-sources/residential_areas.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/residential_areas.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, GYV_KODAS AS code, GYV_PAV as name, PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, GYV_R as created_at FROM residential_areas"
ogrinfo -sql "CREATE UNIQUE INDEX residential_areas_code ON residential_areas(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX residential_municipality_code_and_name ON residential_areas(municipality_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing streets data into SQLite"
curl -f -L --max-redirs 5 --retry 3 -o data-sources/streets.json https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gatves.json
calculate_md5 data-sources/streets.json >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/streets.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, GAT_KODAS AS code, GAT_PAV as name, GAT_PAV_PI AS full_name, GAT_ILGIS as length_m, GYV_KODAS AS residential_area_code, GTV_R AS created_at FROM streets"
ogrinfo -sql "CREATE UNIQUE INDEX streets_code ON streets(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX streets_residential_area_code_and_name ON streets(residential_area_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing addresses data into SQLite"

curl -f -L --max-redirs 5 --retry 3 -o data-sources/addresses-information.psv https://www.registrucentras.lt/aduomenys/?byla=adr_stat_lr.csv
calculate_md5 data-sources/addresses-information.psv >> data-sources/checksums.txt

ogr2ogr -f GPKG data-sources/addresses.gpkg data-sources/addresses-information.psv -nln info

# The complete geojson data with all municipalities is updated only once a year. However,
# when downloaded per municipality, it is updated every month. To ensure we have the latest data,
# this step pulls data for each municipality individually.
echo "Importing address points for each municipality"

curl -sf "https://www.registrucentras.lt/aduomenys/?byla=adr_savivaldybes.csv" | csvcut -d "|" -c "SAV_KODAS" | tail -n +2 | while read -r code; do
  echo "Converting https://www.registrucentras.lt/aduomenys/?byla=adr_gra_$code.json"
  curl -f -L --max-redirs 5 --retry 3 -o "data-sources/addresses-$code.json" "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_$code.json"
  calculate_md5 "data-sources/addresses-$code.json" >> data-sources/checksums.txt

  ogr2ogr -append -f GPKG data-sources/addresses.gpkg "data-sources/addresses-$code.json" -nln points
done

echo "Finishing addresses data import into SQLite"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/addresses.gpkg -lco FID=feature_id -nln addresses \
  -sql "SELECT points.fid AS feature_id, points.geom, points.AOB_KODAS as code, CAST(info.sav_kodas AS integer(8)) AS municipality_code, points.gyv_kodas AS residential_area_code, points.gat_kodas AS street_code, info.nr AS plot_or_building_number, info.pasto_kodas AS postal_code, NULLIF(info.korpuso_nr, '') AS building_block_number, points.AOB_R AS created_at FROM points INNER JOIN info USING (AOB_KODAS) ORDER BY AOB_KODAS"
ogrinfo -sql "CREATE UNIQUE INDEX addresses_code ON addresses(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_municipality_code ON addresses(municipality_code, plot_or_building_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_residential_area_code ON addresses(residential_area_code, plot_or_building_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_street_code ON addresses(street_code, plot_or_building_number)" boundaries.sqlite

echo "Importing rooms"
curl -f -L --max-redirs 5 --retry 3 -o data-sources/rooms.psv https://www.registrucentras.lt/aduomenys/?byla=adr_pat_lr.csv
calculate_md5 data-sources/rooms.psv >> data-sources/checksums.txt
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/rooms.psv -lco FID=code \
  -sql "SELECT CAST(PAT_KODAS AS integer(8)) as code, CAST(AOB_KODAS AS integer(8)) AS address_code, PATALPOS_NR AS room_number, PAT_NUO AS created_at FROM rooms"
ogrinfo -sql "CREATE INDEX rooms_address_code ON rooms(address_code, room_number)" boundaries.sqlite

echo "Finalizing SQLite database"
ogrinfo boundaries.sqlite -sql "VACUUM"

echo "SQLite database created successfully"
