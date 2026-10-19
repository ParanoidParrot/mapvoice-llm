from __future__ import annotations


def resolve_candidate_reviews(
    events: list[dict],
) -> dict:
    independent = [
        event
        for event in events
        if event.get("stage")
        == "independent"
    ]
    adjudications = [
        event
        for event in events
        if event.get("stage")
        == "adjudication"
    ]

    reviewers = {
        event["reviewer_id"]
        for event in independent
    }

    latest_adjudication = (
        adjudications[-1]
        if adjudications
        else None
    )

    if latest_adjudication:
        decision = latest_adjudication[
            "decision"
        ]

        return {
            "status": (
                "verified"
                if decision == "approve"
                else "rejected"
                if decision == "reject"
                else "needs-correction"
            ),
            "native_name": (
                latest_adjudication
                .get("native_name")
                or ""
            ),
            "pronunciation_verified": bool(
                latest_adjudication.get(
                    "pronunciation_approved"
                )
            ),
            "source_verified": bool(
                latest_adjudication.get(
                    "source_approved"
                )
            ),
            "independent_reviewers": (
                len(reviewers)
            ),
            "adjudicated": True,
            "requires_adjudication": False,
        }

    approvals = [
        event
        for event in independent
        if event["decision"] == "approve"
    ]

    if len(reviewers) < 2:
        return {
            "status": (
                "awaiting-first-review"
                if len(reviewers) == 0
                else "awaiting-second-review"
            ),
            "native_name": (
                approvals[-1]
                .get("native_name", "")
                if approvals
                else ""
            ),
            "pronunciation_verified": False,
            "source_verified": False,
            "independent_reviewers": (
                len(reviewers)
            ),
            "adjudicated": False,
            "requires_adjudication": False,
        }

    approved_names = {
        event.get(
            "native_name",
            "",
        ).strip()
        for event in approvals
        if event.get(
            "native_name",
            "",
        ).strip()
    }

    all_approve = (
        len(approvals)
        == len(independent)
    )
    same_name = (
        len(approved_names) == 1
    )
    source_ok = (
        all(
            event.get(
                "source_approved"
            )
            for event in approvals
        )
        if approvals
        else False
    )
    pronunciation_ok = (
        all(
            event.get(
                "pronunciation_approved"
            )
            for event in approvals
        )
        if approvals
        else False
    )

    if (
        all_approve
        and same_name
        and source_ok
    ):
        return {
            "status": "verified",
            "native_name": (
                next(
                    iter(
                        approved_names
                    )
                )
            ),
            "pronunciation_verified": (
                pronunciation_ok
            ),
            "source_verified": True,
            "independent_reviewers": (
                len(reviewers)
            ),
            "adjudicated": False,
            "requires_adjudication": False,
        }

    return {
        "status": "disagreement",
        "native_name": "",
        "pronunciation_verified": False,
        "source_verified": False,
        "independent_reviewers": (
            len(reviewers)
        ),
        "adjudicated": False,
        "requires_adjudication": True,
    }
