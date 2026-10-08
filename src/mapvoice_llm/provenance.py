from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class ProvenanceScore:
    score: int
    status: str
    reasons: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

def score_candidate(row: dict) -> ProvenanceScore:
    score = 0
    reasons: list[str] = []

    if (row.get("source_id") or "").strip():
        score += 20
    else:
        reasons.append("missing_source_id")

    if (row.get("source_license") or "").strip() not in {"", "REVIEW_REQUIRED", "UNKNOWN"}:
        score += 20
    else:
        reasons.append("license_not_cleared")

    if (row.get("source_record_id") or "").strip():
        score += 15
    else:
        reasons.append("missing_source_record_id")

    if (row.get("source_url") or "").strip():
        score += 10
    else:
        reasons.append("missing_source_url")

    if (row.get("source_snapshot_sha256") or "").strip():
        score += 10
    else:
        reasons.append("missing_snapshot_hash")

    if (row.get("latitude") or "").strip() and (row.get("longitude") or "").strip():
        score += 10
    else:
        reasons.append("missing_coordinates")

    if (row.get("native_name") or row.get("kannada_name") or "").strip():
        score += 15
    else:
        reasons.append("missing_native_name")

    status = "complete" if score >= 85 else "partial" if score >= 55 else "insufficient"
    return ProvenanceScore(score=score, status=status, reasons=reasons)
