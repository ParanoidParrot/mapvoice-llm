from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from .benchmark_protocol import BenchmarkProtocol
from .benchmark_slices import classify_example
from .paired_bootstrap import paired_bootstrap_delta


PER_EXAMPLE_METRIC_KEYS = {
    "spoken_form_exact_match": "spoken_exact",
    "entity_exact_match": "entity_exact",
    "mean_character_error_rate": "character_error_rate",
    "valid_json_rate": "valid_json",
}


def _metric(
    row: dict,
    metric: str,
) -> float | None:
    key = PER_EXAMPLE_METRIC_KEYS.get(
        metric,
        metric,
    )
    value = (
        row.get("metrics")
        or {}
    ).get(key)

    if isinstance(
        value,
        bool,
    ):
        return float(
            value
        )

    if isinstance(
        value,
        (int, float),
    ):
        return float(
            value
        )

    return None


def _mean(
    values: list[float],
) -> float | None:
    return (
        sum(values) / len(values)
        if values
        else None
    )


def compare_result_sets(
    *,
    protocol: BenchmarkProtocol,
    first_name: str,
    first_results: list[dict],
    second_name: str,
    second_results: list[dict],
) -> dict:
    first_by_id = {
        row["example_id"]: row
        for row in first_results
    }
    second_by_id = {
        row["example_id"]: row
        for row in second_results
    }

    shared_ids = sorted(
        set(first_by_id)
        & set(second_by_id)
    )

    report = {
        "protocol": (
            protocol.to_dict()
        ),
        "first": first_name,
        "second": second_name,
        "shared_examples": (
            len(shared_ids)
        ),
        "slices": {},
    }

    for slice_id in (
        protocol.required_slices
    ):
        paired = []

        for example_id in shared_ids:
            first = (
                first_by_id[
                    example_id
                ]
            )
            second = (
                second_by_id[
                    example_id
                ]
            )

            source = {
                "target": (
                    first.get(
                        "target"
                    )
                    or {}
                ),
                "metadata": (
                    first.get(
                        "metadata"
                    )
                    or {}
                ),
            }

            if (
                slice_id
                == "entity-held-out"
            ):
                include = True
            else:
                include = (
                    slice_id
                    in classify_example(
                        source
                    )
                )

            if include:
                paired.append(
                    (
                        first,
                        second,
                    )
                )

        slice_report = {
            "examples": (
                len(paired)
            ),
            "metrics": {},
        }

        for metric in (
            protocol.primary_metrics
        ):
            first_values = []
            second_values = []

            for first, second in paired:
                a = _metric(
                    first,
                    metric,
                )
                b = _metric(
                    second,
                    metric,
                )

                if (
                    a is None
                    or b is None
                ):
                    continue

                first_values.append(
                    a
                )
                second_values.append(
                    b
                )

            if not first_values:
                continue

            lower_is_better = (
                metric
                == "mean_character_error_rate"
            )

            bootstrap_first = (
                [-x for x in first_values]
                if lower_is_better
                else first_values
            )
            bootstrap_second = (
                [-x for x in second_values]
                if lower_is_better
                else second_values
            )

            stats = (
                paired_bootstrap_delta(
                    bootstrap_first,
                    bootstrap_second,
                    iterations=(
                        protocol
                        .paired_bootstrap[
                            "iterations"
                        ]
                    ),
                    confidence=(
                        protocol
                        .paired_bootstrap[
                            "confidence"
                        ]
                    ),
                    seed=protocol.seed,
                )
            )

            slice_report[
                "metrics"
            ][metric] = {
                "first_mean": (
                    _mean(
                        first_values
                    )
                ),
                "second_mean": (
                    _mean(
                        second_values
                    )
                ),
                "raw_delta_second_minus_first": (
                    _mean(
                        second_values
                    )
                    - _mean(
                        first_values
                    )
                ),
                "paired_bootstrap": (
                    stats
                ),
                "direction": (
                    "lower"
                    if lower_is_better
                    else "higher"
                ),
            }

        report[
            "slices"
        ][slice_id] = (
            slice_report
        )

    return report


def write_report(
    report: dict,
    path: str | Path,
) -> Path:
    path = Path(
        path
    )
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path
