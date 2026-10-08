from mapvoice_llm.experiment_compare import compare_experiments

def test_experiment_compare_deltas():
    first={"experiment_id":"a","summary":{"entity_exact_match":.5,"mean_character_error_rate":.4}}
    second={"experiment_id":"b","summary":{"entity_exact_match":.8,"mean_character_error_rate":.2}}
    result=compare_experiments(first,second)
    assert round(result['deltas_second_minus_first']['entity_exact_match'],3)==.3
    assert round(result['deltas_second_minus_first']['mean_character_error_rate'],3)==-.2
