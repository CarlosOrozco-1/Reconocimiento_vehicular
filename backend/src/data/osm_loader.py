from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import osmnx as ox


def export_main_roads_from_osm(place_name: str, output_geojson: Path) -> Path:
    """Download drivable network and export principal roads to GeoJSON."""
    graph = ox.graph_from_place(place_name, network_type="drive", simplify=True)
    _, edges = ox.graph_to_gdfs(graph)

    principal = edges[
        edges["highway"].astype(str).str.contains(
            "motorway|trunk|primary|secondary", case=False, regex=True
        )
    ].copy()

    principal = principal.to_crs(4326)
    output_geojson.parent.mkdir(parents=True, exist_ok=True)
    principal.to_file(output_geojson, driver="GeoJSON")
    return output_geojson


def load_departments_geojson(path: Path) -> gpd.GeoDataFrame:
    """Load departments boundaries to GeoDataFrame in EPSG:4326."""
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    return gdf.to_crs(4326)
