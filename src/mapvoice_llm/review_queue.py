from __future__ import annotations
import csv
from pathlib import Path
from .provenance import score_candidate

def build_review_queue(candidate_csv: str | Path, limit: int = 200) -> list[dict]:
    with Path(candidate_csv).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    queue = []
    for row in rows:
        if row.get("annotation_status") in {"reviewed", "rejected"}:
            continue
        score = score_candidate(row)
        item = dict(row)
        item["_provenance_score"] = score.score
        item["_provenance_status"] = score.status
        item["_provenance_reasons"] = "|".join(score.reasons)
        queue.append(item)

    # Prefer rows with native labels and stronger provenance first.
    queue.sort(
        key=lambda row: (
            0 if (row.get("native_name") or row.get("kannada_name") or "").strip() else 1,
            -int(row["_provenance_score"]),
            (row.get("latin_name") or row.get("english_name") or "").casefold(),
        )
    )
    return queue[:limit]
