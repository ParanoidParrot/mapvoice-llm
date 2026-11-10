from __future__ import annotations

from collections import Counter

from .review_consensus import resolve_candidate_reviews


def _latest_independent_by_reviewer(events: list[dict]) -> list[dict]:
    """Return one independent event per reviewer, preserving latest event semantics."""
    latest: dict[str, dict] = {}
    for event in events:
        if event.get("stage") != "independent":
            continue
        reviewer_id = str(event.get("reviewer_id") or "").strip()
        if not reviewer_id:
            continue
        latest[reviewer_id] = event
    return list(latest.values())


def _reviewer_bucket(count: int) -> str:
    if count <= 0:
        return "0"
    if count == 1:
        return "1"
    if count == 2:
        return "2"
    return "3+"


def analyze_candidate_reviews(events: list[dict]) -> dict:
    independent = _latest_independent_by_reviewer(events)
    reviewer_count = len(independent)
    consensus = resolve_candidate_reviews(independent + [
        event for event in events if event.get("stage") == "adjudication"
    ])

    decision_counts = Counter(
        str(event.get("decision") or "")
        for event in independent
        if event.get("decision")
    )
    spelling_counts = Counter(
        str(event.get("spelling_status") or "")
        for event in independent
        if event.get("spelling_status")
    )
    pronunciation_counts = Counter(
        str(event.get("pronunciation_status") or "")
        for event in independent
        if event.get("pronunciation_status")
    )
    familiarity_counts = Counter(
        str(event.get("place_familiarity") or "")
        for event in independent
        if event.get("place_familiarity")
    )

    approved_names = [
        str(event.get("native_name") or "").strip()
        for event in independent
        if event.get("decision") == "approve"
        and str(event.get("native_name") or "").strip()
    ]
    native_name_counts = Counter(approved_names)
    top_native_name = ""
    top_native_name_votes = 0
    if native_name_counts:
        top_native_name, top_native_name_votes = native_name_counts.most_common(1)[0]

    top_decision_votes = 0
    if decision_counts:
        top_decision_votes = decision_counts.most_common(1)[0][1]

    unanimous_decision = (
        reviewer_count >= 2
        and len(decision_counts) == 1
    )
    unanimous_native_name = (
        reviewer_count >= 2
        and decision_counts.get("approve", 0) == reviewer_count
        and len(native_name_counts) == 1
    )
    agreement_ratio = (
        top_decision_votes / reviewer_count
        if reviewer_count
        else 0.0
    )
    native_name_agreement_ratio = (
        top_native_name_votes / reviewer_count
        if reviewer_count
        else 0.0
    )

    status = consensus["status"]
    materialization_ready = status == "verified"
    pronunciation_ready = (
        materialization_ready
        and bool(consensus.get("pronunciation_verified"))
    )
    adjudication_ready = bool(consensus.get("requires_adjudication"))

    return {
        "reviewer_count": reviewer_count,
        "reviewer_bucket": _reviewer_bucket(reviewer_count),
        "reviewer_ids": sorted(
            str(event.get("reviewer_id") or "")
            for event in independent
        ),
        "decision_counts": dict(decision_counts),
        "spelling_status_counts": dict(spelling_counts),
        "pronunciation_status_counts": dict(pronunciation_counts),
        "place_familiarity_counts": dict(familiarity_counts),
        "top_native_name": top_native_name,
        "top_native_name_votes": top_native_name_votes,
        "agreement_ratio": round(agreement_ratio, 4),
        "native_name_agreement_ratio": round(native_name_agreement_ratio, 4),
        "unanimous_decision": unanimous_decision,
        "unanimous_native_name": unanimous_native_name,
        "status": status,
        "requires_adjudication": adjudication_ready,
        "materialization_ready": materialization_ready,
        "pronunciation_ready": pronunciation_ready,
        "pronunciation_verified": bool(consensus.get("pronunciation_verified")),
        "source_verified": bool(consensus.get("source_verified")),
        "adjudicated": bool(consensus.get("adjudicated")),
        "consensus_native_name": str(consensus.get("native_name") or ""),
    }


def summarize_pack_candidates(
    candidates: list[dict],
    by_candidate: dict[str, list[dict]],
) -> dict:
    reviewer_buckets = Counter()
    reviewer_histogram = Counter()
    statuses = Counter()
    total_independent_reviews = 0
    disagreements = 0
    pronunciation_ready = 0
    materialization_ready = 0
    adjudication_ready = 0
    adjudicated = 0
    reviewed_candidates = 0
    details = []

    for candidate in candidates:
        candidate_id = candidate.get("candidate_id", "")
        analysis = analyze_candidate_reviews(by_candidate.get(candidate_id, []))
        count = analysis["reviewer_count"]
        reviewer_buckets[analysis["reviewer_bucket"]] += 1
        reviewer_histogram[str(count)] += 1
        statuses[analysis["status"]] += 1
        total_independent_reviews += count
        if count:
            reviewed_candidates += 1
        if analysis["requires_adjudication"]:
            disagreements += 1
            adjudication_ready += 1
        if analysis["pronunciation_ready"]:
            pronunciation_ready += 1
        if analysis["materialization_ready"]:
            materialization_ready += 1
        if analysis["adjudicated"]:
            adjudicated += 1

        details.append({
            "candidate_id": candidate_id,
            "latin_name": candidate.get("latin_name") or candidate.get("english_name") or "",
            **analysis,
        })

    total_candidates = len(candidates)
    return {
        "candidates": total_candidates,
        "reviewed_candidates": reviewed_candidates,
        "unreviewed_candidates": total_candidates - reviewed_candidates,
        "independent_reviews": total_independent_reviews,
        "reviewer_buckets": {
            "0": reviewer_buckets.get("0", 0),
            "1": reviewer_buckets.get("1", 0),
            "2": reviewer_buckets.get("2", 0),
            "3+": reviewer_buckets.get("3+", 0),
        },
        "reviewer_histogram": dict(sorted(
            reviewer_histogram.items(), key=lambda item: int(item[0])
        )),
        "statuses": dict(statuses),
        "disagreements": disagreements,
        "adjudication_ready": adjudication_ready,
        "adjudicated": adjudicated,
        "materialization_ready": materialization_ready,
        "pronunciation_ready": pronunciation_ready,
        "details": details,
    }
