from mapvoice_llm.hf_export import adapter_manifest, render_model_card


def test_model_card_contains_region_and_base_model():
    manifest = adapter_manifest(
        adapter={'adapter_id': 'mapvoice-blr-kn-v1','adapter_path': '/tmp/adapter','base_model': 'base/model','training_run_id': 'train_1'},
        pack={'pack_id': 'blr-kn','city': 'Bengaluru','state': 'Karnataka','country': 'India','region_language': 'Kannada','region_language_code': 'kn','navigation_languages': ['English','Kannada']},
        metrics={'entity_exact_match': 0.8},
        license_name='other',
    )
    card = render_model_card(manifest=manifest)
    assert 'Bengaluru' in card
    assert 'Kannada' in card
    assert 'base/model' in card
    assert 'entity_exact_match' in card
