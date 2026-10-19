from mapvoice_llm.review_consensus import resolve_candidate_reviews


def review(reviewer, native, pronunciation=False):
    return {
        "candidate_id": "c1",
        "reviewer_id": reviewer,
        "stage": "independent",
        "decision": "approve",
        "native_name": native,
        "pronunciation_approved": pronunciation,
        "source_approved": True,
    }


def test_two_independent_matching_reviews_verify():
    result = resolve_candidate_reviews([
        review("a", "தமிழ்", True),
        review("b", "தமிழ்", True),
    ])

    assert result["status"] == "verified"
    assert result["native_name"] == "தமிழ்"
    assert result["pronunciation_verified"]


def test_disagreement_requires_adjudication():
    result = resolve_candidate_reviews([
        review("a", "தமிழ்"),
        review("b", "வேறு"),
    ])

    assert result["status"] == "disagreement"
    assert result["requires_adjudication"]
