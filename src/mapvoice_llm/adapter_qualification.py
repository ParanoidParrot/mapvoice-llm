from __future__ import annotations

import json
from pathlib import Path


def load_qualification_policy(
    path: str | Path,
) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def _summary(report: dict) -> dict:
    return report.get("summary") or {}


def qualify_adapter(
    *,
    base_report: dict,
    adapter_report: dict,
    dataset_policy: str,
    policy: dict,
) -> dict:
    base = _summary(base_report)
    adapter = _summary(adapter_report)

    spoken_delta = (
        (adapter.get("spoken_form_exact_match") or 0)
        - (base.get("spoken_form_exact_match") or 0)
    )
    cer_delta = (
        (adapter.get("mean_character_error_rate") or 0)
        - (base.get("mean_character_error_rate") or 0)
    )
    entity_delta = (
        (adapter.get("entity_exact_match") or 0)
        - (base.get("entity_exact_match") or 0)
    )

    deltas = {
        "spoken_form_exact_match": spoken_delta,
        "mean_character_error_rate": cer_delta,
        "entity_exact_match": entity_delta,
    }

    results = {}

    for gate_name in ("prototype", "publishable"):
        gate = policy[gate_name]
        checks = {
            "minimum_test_examples": (
                adapter_report.get("examples", 0)
                >= gate["minimum_test_examples"]
            ),
            "minimum_valid_json_rate": (
                (adapter.get("valid_json_rate") or 0)
                >= gate["minimum_valid_json_rate"]
            ),
            "minimum_spoken_exact_delta": (
                spoken_delta
                >= gate["minimum_spoken_exact_delta"]
            ),
            "maximum_cer_delta": (
                cer_delta
                <= gate["maximum_cer_delta"]
            ),
            "maximum_entity_exact_regression": (
                entity_delta
                >= -gate["maximum_entity_exact_regression"]
            ),
        }

        if gate_name == "publishable":
            checks["dataset_policy_allowed"] = (
                dataset_policy
                in gate["allowed_dataset_policies"]
            )

        results[gate_name] = {
            "passed": all(checks.values()),
            "checks": checks,
        }

    return {
        "dataset_policy": dataset_policy,
        "deltas_adapter_minus_base": deltas,
        "prototype": results["prototype"],
        "publishable": results["publishable"],
    }
