from __future__ import annotations

import random
from statistics import mean


def paired_bootstrap_delta(
    first: list[float],
    second: list[float],
    *,
    iterations: int = 1000,
    confidence: float = 0.95,
    seed: int = 20261018,
) -> dict:
    if len(first) != len(second):
        raise ValueError("Paired bootstrap requires equal-length arrays")

    if not first:
        return {
            "n": 0,
            "observed_delta": None,
            "confidence_interval": [None, None],
            "probability_second_better": None,
        }

    observed = mean(second) - mean(first)
    rng = random.Random(seed)
    n = len(first)
    deltas = []

    for _ in range(iterations):
        indices = [rng.randrange(n) for _ in range(n)]
        a = mean(first[i] for i in indices)
        b = mean(second[i] for i in indices)
        deltas.append(b - a)

    deltas.sort()
    alpha = (1.0 - confidence) / 2.0
    low_index = max(0, int(alpha * iterations))
    high_index = min(iterations - 1, int((1.0 - alpha) * iterations) - 1)

    return {
        "n": n,
        "observed_delta": observed,
        "confidence_interval": [
            deltas[low_index],
            deltas[high_index],
        ],
        "probability_second_better": (
            sum(delta > 0 for delta in deltas) / len(deltas)
        ),
    }
