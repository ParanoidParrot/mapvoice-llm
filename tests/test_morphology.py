from mapvoice_llm.morphology import guess_suffix

def test_halli_suffix():
    result = guess_suffix("Marathahalli")
    assert result.suffix == "halli"
    assert result.stem == "maratha"

def test_nagar_suffix():
    assert guess_suffix("Rajajinagar").suffix == "nagar"

def test_no_suffix():
    assert guess_suffix("Yelahanka").suffix is None
