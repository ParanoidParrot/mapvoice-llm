from mapvoice_llm.response_parser import parse_model_output


def test_parse_clean_json():
    result = parse_model_output('{"place_name":"Basavanagudi"}')
    assert result.valid_json
    assert result.data["place_name"] == "Basavanagudi"


def test_parse_json_after_model_prefix():
    result = parse_model_output(
        'Here is the result: {"place_name":"Jayanagar","place_name_kn":"ಜಯನಗರ"}'
    )
    assert result.valid_json
    assert result.data["place_name"] == "Jayanagar"


def test_invalid_output():
    result = parse_model_output("not-json")
    assert not result.valid_json
