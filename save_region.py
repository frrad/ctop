import json
import os
import sys

import geopandas as gpd
from shapely.geometry import MultiPolygon

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")
DEFAULT_TRACTS_FILE = os.path.join(os.path.dirname(__file__), "data", "main_section.txt")


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
  }}).then(r => r.json()).then(searchData => {{
    console.log('search response:', searchData);
    const qs = JSON.stringify({{
      isMapVisible: true,
      mapBounds: {json.dumps(bounds)},
      mapZoom: 14,
      filterState: {{sort: {{value: "globalrelevanceex"}}}},
      isListVisible: true,
      customRegionId: regionId
    }});
    window.location.href = '/homes/for_sale/?searchQueryState=' + encodeURIComponent(qs);
  }});
}}).catch(console.error)"""


def generate_js(geoids, gdf):
    """Generate JS for the given GEOIDs. Returns the JS string or raises an error."""
    selected = gdf[gdf["GEOID"].isin(geoids)]
    missing = set(geoids) - set(selected["GEOID"])
    if missing:
        raise ValueError(f"GEOIDs not found: {', '.join(sorted(missing))}")

    union = selected.union_all()

    if isinstance(union, MultiPolygon):
        raise ValueError("selected tracts are not contiguous")

    # Shapefile coords are (lon, lat), Zillow expects (lat, lon)
    coords = [(lat, lon) for lon, lat in union.exterior.coords]
    return make_fetch_js(coords)


def read_tract_file(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


BEGIN_MARKER = "<!-- BEGIN GENERATED SCRIPTS -->"
END_MARKER = "<!-- END GENERATED SCRIPTS -->"


def update_readme():
    root = os.path.dirname(__file__)
    readme_path = os.path.join(root, "README.md")
    data_dir = os.path.join(root, "data")
    gdf = gpd.read_file(DATA_FILE)

    # Find all tract files
    tract_files = sorted(
        f for f in os.listdir(data_dir) if f.endswith(".txt")
    )

    # Determine the default name from DEFAULT_TRACTS_FILE
    default_name = os.path.splitext(os.path.basename(DEFAULT_TRACTS_FILE))[0]

    # Generate JS for each tract file
    sections = []
    for fname in tract_files:
        name = os.path.splitext(fname)[0]
        path = os.path.join(data_dir, fname)
        geoids = read_tract_file(path)
        try:
            js = generate_js(geoids, gdf)
        except ValueError as e:
            js = None
            error = str(e)

        if name == default_name:
            if js:
                block = f"### {name} (default)\n\n```javascript\n{js}\n```"
            else:
                block = f"### {name} (default)\n\n> Skipped: {error}"
            # Default goes first, not collapsible
            sections.insert(0, block)
        else:
            if js:
                block = (
                    f"<details>\n<summary>{name}</summary>\n\n"
                    f"```javascript\n{js}\n```\n\n</details>"
                )
            else:
                block = (
                    f"<details>\n<summary>{name}</summary>\n\n"
                    f"> Skipped: {error}\n\n</details>"
                )
            sections.append(block)

    generated = BEGIN_MARKER + "\n\n" + "\n\n".join(sections) + "\n\n" + END_MARKER

    with open(readme_path) as f:
        readme = f.read()

    import re
    pattern = re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER)
    if re.search(pattern, readme, re.DOTALL):
        readme = re.sub(pattern, generated, readme, flags=re.DOTALL)
    else:
        print(f"Error: markers not found in {readme_path}", file=sys.stderr)
        sys.exit(1)

    with open(readme_path, "w") as f:
        f.write(readme)

    print(f"Updated {readme_path}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--update-readme":
        update_readme()
        return

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        geoids = read_tract_file(sys.argv[1])
    elif len(sys.argv) > 1:
        geoids = sys.argv[1:]
    else:
        geoids = read_tract_file(DEFAULT_TRACTS_FILE)

    gdf = gpd.read_file(DATA_FILE)

    try:
        js = generate_js(geoids, gdf)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(js)


if __name__ == "__main__":
    main()
