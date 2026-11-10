from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid


VALID_DECISIONS = {
    "approve",
    "reject",
    "needs-correction",
}


@dataclass(frozen=True)
class ReviewEvent:
    review_id: str
    candidate_id: str
    reviewer_id: str
    stage: str
    decision: str
    native_name: str
    pronunciation_approved: bool
    source_approved: bool
    notes: str
    created_at: str
    external_review_id: str = ""
    external_candidate_id: str = ""
    external_source: str = ""
    spelling_status: str = ""
    pronunciation_status: str = ""
    place_familiarity: str = ""
    suggested_native_name: str = ""
    corrected_native_name: str = ""

    @classmethod
    def create(
        cls,
        *,
        candidate_id: str,
        reviewer_id: str,
        stage: str,
        decision: str,
        native_name: str = "",
        pronunciation_approved: bool = False,
        source_approved: bool = False,
        notes: str = "",
        review_id: str | None = None,
        created_at: str | None = None,
        external_review_id: str = "",
        external_candidate_id: str = "",
        external_source: str = "",
        spelling_status: str = "",
        pronunciation_status: str = "",
        place_familiarity: str = "",
        suggested_native_name: str = "",
        corrected_native_name: str = "",
    ) -> "ReviewEvent":
        if decision not in VALID_DECISIONS:
            raise ValueError(
                f"Unsupported review decision: {decision}"
            )

        return cls(
            review_id=review_id or ("rev_" + uuid.uuid4().hex[:14]),
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            stage=stage,
            decision=decision,
            native_name=native_name.strip(),
            pronunciation_approved=pronunciation_approved,
            source_approved=source_approved,
            notes=notes.strip(),
            created_at=created_at or datetime.now(timezone.utc).isoformat(),
            external_review_id=external_review_id,
            external_candidate_id=external_candidate_id,
            external_source=external_source,
            spelling_status=spelling_status,
            pronunciation_status=pronunciation_status,
            place_familiarity=place_familiarity,
            suggested_native_name=suggested_native_name,
            corrected_native_name=corrected_native_name,
        )

    def to_dict(self) -> dict:
        return asdict(self)
