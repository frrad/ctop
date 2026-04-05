import json
import os
import sys

import geopandas as gpd
from shapely.geometry import MultiPolygon

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")
DEFAULT_GEOIDS = ["06075980900", "06075061401"]


def make_fetch_js(coords):
    polygon = "|".join(f"{lat},{lon}" for lat, lon in coords)

    body = json.dumps({
        "operationName": "SaveCustomRegion",
        "variables": {
            "customRegionToSave": {
                "convertToWkt": True,
                "polygon": polygon,
            }
        },
        "query": (
            "mutation SaveCustomRegion($customRegionToSave: SaveCustomRegionInput!) {\n"
            "  saveCustomRegion(customRegionToSave: $customRegionToSave) {\n"
            "    polygon\n"
            "    customRegionId\n"
            "  }\n"
            "}\n"
        ),
    })

    return f"""fetch('https://www.zillow.com/zg-graph?operationName=SaveCustomRegion', {{
  method: 'POST',
  headers: {{
    'accept': '*/*',
    'content-type': 'application/json',
    'x-caller-id': 'search-page-map'
  }},
  body: JSON.stringify({body})
}}).then(r => r.json()).then(console.log).catch(console.error)"""


def main():
    geoids = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_GEOIDS
    gdf = gpd.read_file(DATA_FILE)

    selected = gdf[gdf["GEOID"].isin(geoids)]
    missing = set(geoids) - set(selected["GEOID"])
    if missing:
        print(f"Error: GEOIDs not found: {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    union = selected.union_all()

    if isinstance(union, MultiPolygon):
        print("Error: selected tracts are not contiguous", file=sys.stderr)
        sys.exit(1)

    # Shapefile coords are (lon, lat), Zillow expects (lat, lon)
    coords = [(lat, lon) for lon, lat in union.exterior.coords]

    print(make_fetch_js(coords))


if __name__ == "__main__":
    main()
