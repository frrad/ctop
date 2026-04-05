"""Download CA census tracts and extract SF county tracts as GeoJSON."""

import os
import tempfile
import urllib.request
import zipfile

import geopandas as gpd

URL = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_06_tract.zip"
OUTPUT = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "ca_tracts.zip")
        print(f"Downloading {URL} ...")
        urllib.request.urlretrieve(URL, zip_path)
        print("Extracting...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmpdir)

        shp = [f for f in os.listdir(tmpdir) if f.endswith(".shp")][0]
        gdf = gpd.read_file(os.path.join(tmpdir, shp))

    sf = gdf[gdf["COUNTYFP"] == "075"]
    print(f"Found {len(sf)} tracts in SF county")

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    sf.to_file(OUTPUT, driver="GeoJSON")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
