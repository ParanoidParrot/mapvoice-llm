from mapvoice_llm.data_quality import get_policy, evaluate_entity
from mapvoice_llm.regional_entity import RegionalEntity


def entity(**kwargs):
    values = {
        "entity_id": "x",
        "latin_name": "Example",
        "native_name": "Native",
        "entity_type": "locality",
        "city": "City",
        "language": "Language",
        "verification_status": "unverified",
        "pronunciation_verified": False,
        "source_name": "",
    }
    values.update(kwargs)
    return RegionalEntity(**values)


def test_reviewed_policy_requires_review_and_source():
    ok, reasons = evaluate_entity(
        entity(),
        get_policy("reviewed"),
    )
    assert not ok
    assert "verification_status_below_policy" in reasons
    assert "missing_source" in reasons


def test_verified_policy_accepts_verified_sourced_entity():
    ok, reasons = evaluate_entity(
        entity(
            verification_status="verified",
            source_name="source",
        ),
        get_policy("verified"),
    )
    assert ok
    assert reasons == []
