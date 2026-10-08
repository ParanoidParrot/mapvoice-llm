from mapvoice_llm.runtime_compat import required_training_package_checks


def test_dependency_checks_include_tokenizer_dependencies():
    messages = [
        item.message
        for item in required_training_package_checks()
    ]

    assert any("protobuf" in message for message in messages)
    assert any("sentencepiece" in message for message in messages)
