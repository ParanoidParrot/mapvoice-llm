from __future__ import annotations
import csv
import json
from pathlib import Path

def read_csv_rows(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def _point_coords(geometry: dict | None) -> tuple[str, str]:
    if not geometry or geometry.get("type") != "Point":
        return "", ""
    coords = geometry.get("coordinates") or []
    if len(coords) < 2:
        return "", ""
    return str(coords[1]), str(coords[0])

def read_geojson_rows(
    path: str | Path,
    *,
    language_code: str,
) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    features = data.get("features", [])
    rows = []

    for feature in features:
        props = feature.get("properties") or {}
        lat, lon = _point_coords(feature.get("geometry"))

        # Common OSM/GeoJSON naming conventions.
        native = (
            props.get(f"name:{language_code}")
            or props.get("native_name")
            or ""
        )
        latin = (
            props.get("name:en")
            or props.get("name")
            or props.get("latin_name")
            or ""
        )

        rows.append({
            "latin_name": latin,
            "native_name": native,
            "entity_type": props.get("place") or props.get("highway") or props.get("entity_type") or "locality",
            "source_record_id": props.get("@id") or props.get("osm_id") or feature.get("id") or "",
            "alternate_names": props.get("alt_name") or props.get("name:en") or "",
            "latitude": props.get("lat") or lat,
            "longitude": props.get("lon") or lon,
            "source_url": props.get("source_url") or "",
            "notes": "",
        })
    return rows
