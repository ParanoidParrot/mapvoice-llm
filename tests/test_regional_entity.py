from mapvoice_llm.regional_entity import from_legacy_entity_row


def test_legacy_entity_maps_to_generic():
    entity = from_legacy_entity_row(
        {
            "entity_id": "blr_1",
            "english_name": "Jayanagar",
            "kannada_name": "ಜಯನಗರ",
            "entity_type": "locality",
            "city": "Bengaluru",
            "language": "Kannada",
            "verification_status": "reviewed",
            "pronunciation_verified": "false",
        },
        language_code="kn",
    )

    assert entity.latin_name == "Jayanagar"
    assert entity.native_name == "ಜಯನಗರ"
    assert entity.language_code == "kn"
