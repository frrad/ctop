import json
import os
import sys

import geopandas as gpd
from shapely.geometry import MultiPolygon

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")
DEFAULT_GEOIDS = ["06075980900", "06075061401"]


def make_fetch_js(coords):
    polygon = "|".join(f"{lat},{lon}" for lat, lon in coords)

    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]
    bounds = {
        "west": min(lons),
        "east": max(lons),
        "south": min(lats),
        "north": max(lats),
    }

    save_body = json.dumps({
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

    search_body_template = json.dumps({
        "searchQueryState": {
            "isMapVisible": True,
            "mapBounds": bounds,
            "filterState": {"sortSelection": {"value": "globalrelevanceex"}},
            "isListVisible": True,
            "mapZoom": 14,
            "customRegionId": "__REGION_ID__",
        },
        "wants": {
            "cat1": ["listResults", "mapResults"],
            "cat2": ["total"],
            "abTrials": ["total"],
        },
        "requestId": 1,
        "isDebugRequest": False,
    })

    return f"""fetch('https://www.zillow.com/zg-graph?operationName=SaveCustomRegion', {{
  method: 'POST',
  headers: {{
    'accept': '*/*',
    'content-type': 'application/json',
    'x-caller-id': 'search-page-map'
  }},
  body: JSON.stringify({save_body})
}}).then(r => r.json()).then(data => {{
  const regionId = data.data.saveCustomRegion.customRegionId;
  console.log('customRegionId:', regionId);
  const body = JSON.parse('{search_body_template}'.replace('__REGION_ID__', regionId));
  return fetch('https://www.zillow.com/async-create-search-page-state', {{
    method: 'PUT',
    headers: {{
      'accept': '*/*',
      'content-type': 'application/json'
    }},
    body: JSON.stringify(body)
  }});
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
