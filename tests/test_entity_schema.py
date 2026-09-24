from mapvoice_llm.entity_schema import EntityRecord

def test_verification_properties():
    row = EntityRecord(
        entity_id="x",
        english_name="Example",
        kannada_name="ಉದಾಹರಣೆ",
        entity_type="locality",
        city="Bengaluru",
        language="Kannada",
        verification_status="verified",
        pronunciation_verified="true",
    )
    assert row.verified
    assert row.pronunciation_is_verified
