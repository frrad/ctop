# ctop

Generate Zillow custom region boundaries from census tracts.

Takes one or more SF census tract GEOIDs, computes their polygon union, and outputs a `fetch()` snippet you can paste into Chrome DevTools on zillow.com.

## Setup

```
uv venv
uv pip install -r requirements.txt
```

## Usage

```
# Default tracts (06075980900, 06075061401)
.venv/bin/python save_region.py

# Specify tracts
.venv/bin/python save_region.py 06075020602 06075020500
```

Paste the output into the Chrome DevTools console while on zillow.com.

To copy directly to clipboard (Wayland):

```
.venv/bin/python save_region.py | wl-copy
```

## Regenerating tract data

The SF county tract boundaries (`data/sf_tracts.geojson`) are checked in. To regenerate from the Census Bureau source:

```
.venv/bin/python prepare_data.py
```
