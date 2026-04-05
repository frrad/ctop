"""Build contiguous cluster txt files from a Datawrapper CTIP1 CSV.

The CSV comes from the map embedded in this Substack post about SFUSD
school assignment tiebreakers:
https://sfeducation.substack.com/p/what-new-public-data-tells-us-about

The specific Datawrapper map is:
https://datawrapper.dwcdn.net/9fX5e/2/
and the CSV can be downloaded from:
https://datawrapper.dwcdn.net/9fX5e/2/dataset.csv

The CSV has columns TRACTCE (census tract code) and CTIP1 (TRUE/FALSE).
This script filters to CTIP1=TRUE, groups into contiguous clusters using
the SF tract geometries, and writes one txt file per cluster.
"""

import csv
import os
import sys

import geopandas as gpd

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sf_tracts.geojson")


def load_ctip1_geoids(csv_path):
    geoids = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row["CTIP1"] == "TRUE":
                geoids.append(f"06075{int(row['TRACTCE']):06d}")
    return geoids


def cluster_tracts(gdf, geoids):
    selected = gdf[gdf["GEOID"].isin(geoids)].copy()
    missing = set(geoids) - set(selected["GEOID"])
    if missing:
        print(f"Warning: GEOIDs not found: {', '.join(sorted(missing))}", file=sys.stderr)

    clusters = []
    remaining = set(selected.index)
    while remaining:
        seed = remaining.pop()
        cluster = {seed}
        frontier = [seed]
        while frontier:
            current = frontier.pop()
            geom = selected.loc[current, "geometry"]
            for idx in list(remaining):
                if geom.touches(selected.loc[idx, "geometry"]) or geom.intersects(
                    selected.loc[idx, "geometry"]
                ):
                    cluster.add(idx)
                    remaining.discard(idx)
                    frontier.append(idx)
        clusters.append(sorted(selected.loc[list(cluster), "GEOID"].tolist()))

    return sorted(clusters, key=len, reverse=True)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <ctip1_dataset.csv>", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]
    geoids = load_ctip1_geoids(csv_path)
    print(f"Found {len(geoids)} CTIP1 tracts")

    gdf = gpd.read_file(DATA_FILE)
    clusters = cluster_tracts(gdf, geoids)
    print(f"Found {len(clusters)} contiguous clusters")

    for i, tracts in enumerate(clusters):
        filename = f"ctip1_cluster{i}.txt"
        with open(filename, "w") as f:
            for t in tracts:
                f.write(t + "\n")
        print(f"  {filename}: {len(tracts)} tracts")


if __name__ == "__main__":
    main()
