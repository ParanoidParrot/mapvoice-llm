from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_ingestion_manifest(
    *,
    project_root: Path,
    pack_id: str,
    source_id: str,
    input_path: Path,
    stats: dict,
) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = sha256_file(input_path)
    ingest_id = f"{pack_id}_{source_id}_{timestamp}_{digest[:8]}"

    out = project_root / "data" / "provenance" / "ingestions" / f"{ingest_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "ingestion_id": ingest_id,
        "pack_id": pack_id,
        "source_id": source_id,
        "input_file": str(input_path),
        "input_sha256": digest,
        "retrieved_at": timestamp,
        "stats": stats,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
