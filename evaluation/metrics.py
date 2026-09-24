from __future__ import annotations


def levenshtein_distance(reference: str, hypothesis: str) -> int:
    previous = list(range(len(hypothesis) + 1))

    for i, ref_char in enumerate(reference, start=1):
        current = [i]
        for j, hyp_char in enumerate(hypothesis, start=1):
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (ref_char != hyp_char)
            current.append(min(insertion, deletion, substitution))
        previous = current

    return previous[-1]


def character_error_rate(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein_distance(reference, hypothesis) / len(reference)


def exact_match(reference: str | None, hypothesis: str | None) -> float:
    return float((reference or "") == (hypothesis or ""))


def normalized_exact_match(reference: str | None, hypothesis: str | None) -> float:
    def normalize(value: str | None) -> str:
        return " ".join((value or "").strip().casefold().split())

    return float(normalize(reference) == normalize(hypothesis))
