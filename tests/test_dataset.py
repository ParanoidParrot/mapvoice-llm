from mapvoice_llm.dataset import Entity, generate_examples, split_by_entity


def test_examples_generated_per_entity():
    entities = [
        Entity(
            entity_id="blr_001",
            english_name="Basavanagudi",
            kannada_name="ಬಸವನಗುಡಿ",
            entity_type="locality",
            city="Bengaluru",
            language="Kannada",
        )
    ]
    examples = generate_examples(entities)
    assert len(examples) >= 4
    assert all(x["entity_id"] == "blr_001" for x in examples)


def test_split_never_leaks_entity():
    entities = [
        Entity(
            entity_id=f"blr_{i:03}",
            english_name=f"Place{i}",
            kannada_name=f"ಸ್ಥಳ{i}",
            entity_type="locality",
            city="Bengaluru",
            language="Kannada",
        )
        for i in range(20)
    ]

    examples = generate_examples(entities)
    train, validation, test = split_by_entity(examples)

    train_ids = {x["entity_id"] for x in train}
    validation_ids = {x["entity_id"] for x in validation}
    test_ids = {x["entity_id"] for x in test}

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)
