import json
import os
import sys

import geopandas as gpd
from shapely.geometry import MultiPolygon

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")


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
  body: {body}
}}).then(r => r.json()).then(console.log).catch(console.error)"""


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} GEOID [GEOID ...]", file=sys.stderr)
        print(f"Example: {sys.argv[0]} 06075010100 06075010200", file=sys.stderr)
        sys.exit(1)

    geoids = sys.argv[1:]
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
