from mapvoice_llm.review_analytics import (
    analyze_candidate_reviews,
    summarize_pack_candidates,
)


def review(reviewer, native="ಬೆಂಗಳೂರು", *, decision="approve", pronunciation=True):
    return {
        "candidate_id": "c1",
        "reviewer_id": reviewer,
        "stage": "independent",
        "decision": decision,
        "native_name": native,
        "pronunciation_approved": pronunciation,
        "source_approved": decision == "approve",
        "spelling_status": "correct" if decision == "approve" else "unsure",
        "pronunciation_status": "correct" if pronunciation else "unsure",
        "place_familiarity": "know",
    }


def test_three_matching_reviewers_are_counted_and_ready():
    result = analyze_candidate_reviews([
        review("a"), review("b"), review("c"),
    ])
    assert result["reviewer_count"] == 3
    assert result["reviewer_bucket"] == "3+"
    assert result["status"] == "verified"
    assert result["materialization_ready"] is True
    assert result["pronunciation_ready"] is True
    assert result["agreement_ratio"] == 1.0


def test_third_reviewer_dissent_requires_adjudication():
    result = analyze_candidate_reviews([
        review("a"),
        review("b"),
        review("c", decision="needs-correction", pronunciation=False),
    ])
    assert result["reviewer_count"] == 3
    assert result["status"] == "disagreement"
    assert result["requires_adjudication"] is True
    assert result["materialization_ready"] is False
    assert result["agreement_ratio"] == 0.6667


def test_pack_summary_supports_zero_one_two_and_three_plus_reviewers():
    candidates = [
        {"candidate_id": "c0", "latin_name": "Zero"},
        {"candidate_id": "c1", "latin_name": "One"},
        {"candidate_id": "c2", "latin_name": "Two"},
        {"candidate_id": "c3", "latin_name": "Three"},
    ]
    by_candidate = {
        "c1": [{**review("a"), "candidate_id": "c1"}],
        "c2": [
            {**review("a"), "candidate_id": "c2"},
            {**review("b"), "candidate_id": "c2"},
        ],
        "c3": [
            {**review("a"), "candidate_id": "c3"},
            {**review("b"), "candidate_id": "c3"},
            {**review("c"), "candidate_id": "c3"},
        ],
    }
    result = summarize_pack_candidates(candidates, by_candidate)
    assert result["reviewer_buckets"] == {"0": 1, "1": 1, "2": 1, "3+": 1}
    assert result["reviewer_histogram"] == {"0": 1, "1": 1, "2": 1, "3": 1}
    assert result["materialization_ready"] == 2
    assert result["pronunciation_ready"] == 2


def test_latest_review_per_reviewer_prevents_double_counting():
    first = review("a")
    second = review("a", decision="needs-correction", pronunciation=False)
    result = analyze_candidate_reviews([first, second])
    assert result["reviewer_count"] == 1
    assert result["decision_counts"] == {"needs-correction": 1}
