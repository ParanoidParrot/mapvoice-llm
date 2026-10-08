from mapvoice_llm.artifact_naming import default_adapter_id


def test_default_adapter_id():
    assert default_adapter_id(pack_id='BLR-KN', version='v1') == 'mapvoice-blr-kn-v1'
