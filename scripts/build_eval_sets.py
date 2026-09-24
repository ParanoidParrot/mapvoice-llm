from __future__ import annotations

import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
OUT = PROJECT_ROOT / "data" / "evaluation"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    main_entities = read_csv(RAW / "bengaluru_entities_v0.1.csv")
    hard_entities = read_csv(RAW / "blr_kn_hard_v1.csv")

    known = []
    for row in main_entities:
        known.append(
            {
                "suite": "lexicon-known",
                "entity_id": row["entity_id"],
                "english_name": row["english_name"],
                "kannada_name": row["kannada_name"],
                "entity_type": row["entity_type"],
                "verified": row["verified"].lower() == "true",
                "instruction": f"Continue towards {row['english_name']}.",
            }
        )

    hard = []
    for row in hard_entities:
        hard.append(
            {
                "suite": "morphological-hard",
                "entity_id": row["entity_id"],
                "english_name": row["english_name"],
                "kannada_name": row["kannada_name"],
                "entity_type": row["entity_type"],
                "status": row["status"],
                "instruction": f"Turn left towards {row['english_name']}.",
            }
        )

    write_jsonl(known, OUT / "lexicon_known.jsonl")
    write_jsonl(hard, OUT / "morphological_hard.jsonl")

    manifest = {
        "lexicon_known": len(known),
        "morphological_hard": len(hard),
        "warning": (
            "These sets are scaffolding only. Any row not manually verified must not be "
            "treated as authoritative pronunciation ground truth."
        ),
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
