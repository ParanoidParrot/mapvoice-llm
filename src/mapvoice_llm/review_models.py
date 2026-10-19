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
    ) -> "ReviewEvent":
        if decision not in VALID_DECISIONS:
            raise ValueError(
                f"Unsupported review decision: {decision}"
            )

        return cls(
            review_id="rev_" + uuid.uuid4().hex[:14],
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            stage=stage,
            decision=decision,
            native_name=native_name.strip(),
            pronunciation_approved=pronunciation_approved,
            source_approved=source_approved,
            notes=notes.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict:
        return asdict(self)
