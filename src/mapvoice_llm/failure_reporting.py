from __future__ import annotations

from collections import Counter


def summarize_failures(results: list[dict]) -> dict:
    counter = Counter()
    examples_with_failures = 0

    for row in results:
        failures = row.get("failures") or []
        if failures:
            examples_with_failures += 1

        for failure in failures:
            counter[failure["code"]] += 1

    return {
        "examples_with_failures": examples_with_failures,
        "failure_counts": dict(counter.most_common()),
    }
