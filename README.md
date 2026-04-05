# ctop

Generate Zillow custom region boundaries from SF census tracts.

Takes census tract GEOIDs, computes their polygon union, and outputs a `fetch()` snippet you can paste into Chrome DevTools on zillow.com. The snippet saves the custom region, creates the search page state, and navigates to the results.

## Setup

```
uv venv
uv pip install -r requirements.txt
```

## Usage

```
# Default: main CTIP1 section (25 tracts)
.venv/bin/python save_region.py

# Use a specific tract file
.venv/bin/python save_region.py data/tenderloin.txt

# Specify individual GEOIDs
.venv/bin/python save_region.py 06075020602 06075020500
```

To copy directly to clipboard (Wayland):

```
.venv/bin/python save_region.py | wl-copy
```

Paste the output into the Chrome DevTools console while on zillow.com.

**Note:** Zillow may reject regions with complex polygons (many tracts merged together) when you try to save them to your account. The search works fine in-session, but saving can fail with a "too complex" error.

## Tract files

Pre-built tract lists based on SFUSD CTIP1 tiebreaker areas (from [this Substack post](https://sfeducation.substack.com/p/what-new-public-data-tells-us-about)):

- `data/main_section.txt` — 25 tracts, largest contiguous CTIP1 area (default)
- `data/tenderloin.txt` — 6 tracts
- `data/sunnydale.txt` — 2 tracts
- `data/treasure_island.txt` — 1 tract (broken: MultiPolygon geometry)

## Rebuilding cluster files

To regenerate the cluster files from the Datawrapper CSV:

```
.venv/bin/python build_clusters.py data/ctip1_dataset.csv
```

## Regenerating tract geometries

The SF county tract boundaries (`data/sf_tracts.geojson`) are checked in. To regenerate from the Census Bureau source:

```
.venv/bin/python prepare_data.py
```
