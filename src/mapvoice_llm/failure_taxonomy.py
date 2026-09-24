from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Failure:
    code: str
    label: str
    severity: str
    details: str


FAILURE_LABELS = {
    "invalid_json": "Malformed model JSON",
    "missing_entity": "Entity not detected",
    "wrong_entity": "Wrong entity",
    "missing_kannada": "Kannada form missing",
    "wrong_kannada": "Wrong Kannada form",
    "missing_spoken_form": "Spoken form missing",
    "wrong_spoken_form": "Spoken form mismatch",
    "high_cer": "High character error rate",
    "suffix_failure": "Suffix/morphology failure",
    "unknown_entity": "Unknown entity",
}


def classify_failure(
    *,
    target: dict,
    prediction: dict,
    valid_json: bool = True,
    cer: float = 0.0,
    metadata: dict | None = None,
) -> list[Failure]:
    failures: list[Failure] = []
    metadata = metadata or {}

    if not valid_json:
        failures.append(
            Failure(
                code="invalid_json",
                label=FAILURE_LABELS["invalid_json"],
                severity="error",
                details="Model output was not parseable as valid JSON.",
            )
        )

    target_entity = target.get("place_name")
    predicted_entity = (
        prediction.get("place_name")
        or prediction.get("detected_entity")
    )

    if not predicted_entity:
        failures.append(
            Failure(
                code="missing_entity",
                label=FAILURE_LABELS["missing_entity"],
                severity="error",
                details="No entity was returned for the navigation instruction.",
            )
        )
    elif target_entity and predicted_entity != target_entity:
        failures.append(
            Failure(
                code="wrong_entity",
                label=FAILURE_LABELS["wrong_entity"],
                severity="error",
                details=f"Expected '{target_entity}', got '{predicted_entity}'.",
            )
        )

    target_kn = target.get("place_name_kn")
    predicted_kn = prediction.get("place_name_kn")

    if target_kn and not predicted_kn:
        failures.append(
            Failure(
                code="missing_kannada",
                label=FAILURE_LABELS["missing_kannada"],
                severity="error",
                details="Expected a Kannada-script entity form but none was produced.",
            )
        )
    elif target_kn and predicted_kn and target_kn != predicted_kn:
        failures.append(
            Failure(
                code="wrong_kannada",
                label=FAILURE_LABELS["wrong_kannada"],
                severity="warning",
                details=f"Expected '{target_kn}', got '{predicted_kn}'.",
            )
        )

    target_spoken = (
        target.get("spoken_form")
        or target.get("pronunciation_form")
    )
    predicted_spoken = (
        prediction.get("spoken_form")
        or prediction.get("pronunciation_form")
    )

    if target_spoken and not predicted_spoken:
        failures.append(
            Failure(
                code="missing_spoken_form",
                label=FAILURE_LABELS["missing_spoken_form"],
                severity="error",
                details="No spoken/pronunciation target was produced.",
            )
        )
    elif target_spoken and predicted_spoken and target_spoken != predicted_spoken:
        failures.append(
            Failure(
                code="wrong_spoken_form",
                label=FAILURE_LABELS["wrong_spoken_form"],
                severity="warning",
                details=f"Expected '{target_spoken}', got '{predicted_spoken}'.",
            )
        )

    if cer >= 0.5:
        failures.append(
            Failure(
                code="high_cer",
                label=FAILURE_LABELS["high_cer"],
                severity="warning",
                details=f"Character error rate is {cer:.3f}.",
            )
        )

    suffix = metadata.get("suffix")
    if suffix and target_spoken and predicted_spoken:
        normalized_suffix = suffix.casefold()
        if normalized_suffix not in str(predicted_entity or "").casefold():
            failures.append(
                Failure(
                    code="suffix_failure",
                    label=FAILURE_LABELS["suffix_failure"],
                    severity="warning",
                    details=f"Expected suffix pattern '{suffix}' was not preserved in entity output.",
                )
            )

    if (
        metadata.get("suite") in {"morphological-hard", "generated-hard-holdout"}
        and not predicted_entity
    ):
        failures.append(
            Failure(
                code="unknown_entity",
                label=FAILURE_LABELS["unknown_entity"],
                severity="warning",
                details="Hard-set entity was not recognized.",
            )
        )

    # Deduplicate by code while preserving order.
    deduped = []
    seen = set()
    for failure in failures:
        if failure.code in seen:
            continue
        seen.add(failure.code)
        deduped.append(failure)

    return deduped
