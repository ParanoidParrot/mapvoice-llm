from mapvoice_llm.provenance import score_candidate

def test_complete_candidate_scores_high():
    result = score_candidate({
        "source_id":"osm","source_license":"ODbL-1.0","source_record_id":"n1",
        "source_url":"https://example.com","source_snapshot_sha256":"abc",
        "latitude":"1","longitude":"2","native_name":"தமிழ்"
    })
    assert result.score == 100
    assert result.status == "complete"
