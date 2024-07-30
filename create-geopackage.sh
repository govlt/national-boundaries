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

download_data_source_and_md5() {
  local filename="$1"
  local url="$2"

  if ! curl -f -L --max-redirs 5 --retry 3 -o "data-sources/$filename" "$url"; then
    echo "Download failed."
    return 1
  fi

  # Calculate the MD5 checksum of the downloaded file
  calculate_md5 data-sources/"$filename" >> data-sources/data-source-checksums.txt
}

echo "Starting data processing"

rm -rf boundaries-4326.gpkg data-sources

mkdir -p data-sources

echo "Importing counties data into GeoPackage"
download_data_source_and_md5 counties.json "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json"
ogr2ogr boundaries-4326.gpkg data-sources/counties.json -lco FID=feature_id -xyRes 0.000001 -t_srs EPSG:4326 \
  -sql "SELECT FID AS feature_id, CAST(APS_KODAS AS integer(8)) AS code, APS_PAV as name, APS_PLOTAS as area_ha, APS_R AS created_at FROM counties"

echo "Importing municipalities data into GeoPackage"
download_data_source_and_md5 municipalities.json "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json"
ogr2ogr -append boundaries-4326.gpkg data-sources/municipalities.json -lco FID=feature_id -xyRes 0.000001 -t_srs EPSG:4326 \
  -sql "SELECT FID AS feature_id, CAST(SAV_KODAS AS integer(8)) AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, CAST(APS_KODAS AS integer(8)) as county_code, SAV_R AS created_at FROM municipalities"

echo "Importing elderships data into GeoPackage"
download_data_source_and_md5 elderships.json "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json"
ogr2ogr -append boundaries-4326.gpkg data-sources/elderships.json -lco FID=feature_id -xyRes 0.000001 -t_srs EPSG:4326 \
  -sql "SELECT FID AS feature_id, CAST(SEN_KODAS AS integer(8)) AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, SEN_R AS created_at FROM elderships"

echo "Importing residential areas data into GeoPackage"
download_data_source_and_md5 residential_areas.json "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json"
ogr2ogr -append boundaries-4326.gpkg data-sources/residential_areas.json -lco FID=feature_id -xyRes 0.000001 -t_srs EPSG:4326 \
  -sql "SELECT FID AS feature_id, GYV_KODAS AS code, GYV_PAV as name, PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, GYV_R as created_at FROM residential_areas"

echo "Importing streets data into GeoPackage"
download_data_source_and_md5 streets.json "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gatves.json"
ogr2ogr -append boundaries-4326.gpkg data-sources/streets.json -lco FID=feature_id -xyRes 0.000001 -t_srs EPSG:4326 \
  -sql "SELECT FID AS feature_id, GAT_KODAS AS code, GAT_PAV as name, GAT_PAV_PI AS full_name, GAT_ILGIS as length_m, GYV_KODAS AS residential_area_code, GTV_R AS created_at FROM streets"

echo "Finalizing GeoPackage"
ogrinfo boundaries-4326.gpkg -sql "VACUUM"

echo "Copying GeoPackage to data folder"

mkdir -p data
cp boundaries-4326.gpkg data/boundaries-4326.gpkg

echo "GeoPackage database created successfully"

