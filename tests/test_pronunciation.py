from mapvoice_llm.pronunciation import build_target, contains_kannada


def test_contains_kannada():
    assert contains_kannada("ಜಯನಗರ")
    assert not contains_kannada("Jayanagar")


def test_native_script_target():
    target = build_target(kannada_name="ಜಯನಗರ", fallback_name="Jayanagar")
    assert target.spoken_form == "ಜಯನಗರ"
    assert target.representation == "native-script"
    assert target.phonetic_form is None


def test_fallback_target():
    target = build_target(kannada_name="", fallback_name="Jayanagar")
    assert target.spoken_form == "Jayanagar"
    assert target.representation == "english-script-fallback"
