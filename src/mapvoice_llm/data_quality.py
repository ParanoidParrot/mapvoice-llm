from __future__ import annotations

from dataclasses import dataclass

from .regional_entity import RegionalEntity


VERIFICATION_RANK = {
    "unverified": 0,
    "reviewed": 1,
    "verified": 2,
}


@dataclass(frozen=True)
class DatasetPolicy:
    policy_id: str
    require_native_name: bool = True
    minimum_verification_status: str = "unverified"
    require_pronunciation_verified: bool = False
    require_source: bool = False

    def to_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "require_native_name": self.require_native_name,
            "minimum_verification_status": self.minimum_verification_status,
            "require_pronunciation_verified": self.require_pronunciation_verified,
            "require_source": self.require_source,
        }


POLICIES = {
    "labeled": DatasetPolicy(
        policy_id="labeled",
        require_native_name=True,
        minimum_verification_status="unverified",
    ),
    "reviewed": DatasetPolicy(
        policy_id="reviewed",
        require_native_name=True,
        minimum_verification_status="reviewed",
        require_source=True,
    ),
    "verified": DatasetPolicy(
        policy_id="verified",
        require_native_name=True,
        minimum_verification_status="verified",
        require_source=True,
    ),
    "pronunciation-verified": DatasetPolicy(
        policy_id="pronunciation-verified",
        require_native_name=True,
        minimum_verification_status="verified",
        require_pronunciation_verified=True,
        require_source=True,
    ),
}


def get_policy(policy_id: str) -> DatasetPolicy:
    try:
        return POLICIES[policy_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown dataset policy: {policy_id}"
        ) from exc


def evaluate_entity(
    entity: RegionalEntity,
    policy: DatasetPolicy,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if (
        policy.require_native_name
        and not entity.native_name.strip()
    ):
        reasons.append("missing_native_name")

    entity_rank = VERIFICATION_RANK.get(
        entity.verification_status,
        -1,
    )
    required_rank = VERIFICATION_RANK[
        policy.minimum_verification_status
    ]

    if entity_rank < required_rank:
        reasons.append(
            "verification_status_below_policy"
        )

    if (
        policy.require_pronunciation_verified
        and not entity.pronunciation_verified
    ):
        reasons.append(
            "pronunciation_not_verified"
        )

    if (
        policy.require_source
        and not entity.source_name.strip()
    ):
        reasons.append("missing_source")

    return not reasons, reasons


def filter_entities(
    entities: list[RegionalEntity],
    policy: DatasetPolicy,
) -> tuple[list[RegionalEntity], dict]:
    included = []
    excluded = []
    reason_counts: dict[str, int] = {}

    for entity in entities:
        accepted, reasons = evaluate_entity(
            entity,
            policy,
        )
        if accepted:
            included.append(entity)
            continue

        excluded.append({
            "entity_id": entity.entity_id,
            "latin_name": entity.latin_name,
            "reasons": reasons,
        })

        for reason in reasons:
            reason_counts[reason] = (
                reason_counts.get(reason, 0) + 1
            )

    return included, {
        "policy": policy.to_dict(),
        "source_entities": len(entities),
        "included_entities": len(included),
        "excluded_entities": len(excluded),
        "exclusion_reason_counts": reason_counts,
        "excluded": excluded,
    }
