from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.bulk_ingest import ingest_rows
from mapvoice_llm.pack_context import load_pack_context
from mapvoice_llm.source_readers import read_csv_rows, read_geojson_rows
from mapvoice_llm.source_registry import SourceRegistry

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["csv", "geojson"], required=True)
    args = parser.parse_args()

    context = load_pack_context(PROJECT_ROOT, args.pack_id)
    source = SourceRegistry(PROJECT_ROOT / "configs/source_registry.json").get(args.source_id)
    input_path = Path(args.input)

    if args.format == "csv":
        rows = read_csv_rows(input_path)
    else:
        rows = read_geojson_rows(input_path, language_code=context.pack.region_language_code)

    result = ingest_rows(
        project_root=PROJECT_ROOT,
        context=context,
        source=source,
        input_path=input_path,
        rows=rows,
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
