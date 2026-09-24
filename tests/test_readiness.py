import csv

from mapvoice_llm.readiness import training_readiness


ENTITY_FIELDS = [
    "entity_id","english_name","kannada_name","entity_type",
    "city","language","alternate_spellings","morphemes","suffix",
    "verification_status","pronunciation_verified",
    "source_name","source_url","source_type","reviewer","notes",
]

CANDIDATE_FIELDS = [
    "candidate_id","english_name","entity_type","city","region_language",
    "annotation_status","kannada_name","source_name","source_url","notes",
]


def test_training_readiness_not_ready(tmp_path):
    entities = tmp_path / "entities.csv"
    with entities.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTITY_FIELDS)
        writer.writeheader()
        writer.writerow({
            "entity_id":"x","english_name":"Example","kannada_name":"ಉದಾಹರಣೆ",
            "entity_type":"locality","city":"Bengaluru","language":"Kannada",
            "alternate_spellings":"","morphemes":"","suffix":"",
            "verification_status":"unverified","pronunciation_verified":"false",
            "source_name":"","source_url":"","source_type":"",
            "reviewer":"","notes":"",
        })

    candidates = tmp_path / "candidates.csv"
    with candidates.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerow({
            "candidate_id":"c","english_name":"Candidate","entity_type":"locality",
            "city":"Bengaluru","region_language":"Kannada",
            "annotation_status":"candidate","kannada_name":"",
            "source_name":"","source_url":"","notes":"",
        })

    result = training_readiness(entities, candidates)

    assert result["ready_for_first_strict_training"] is False
    assert result["entities_verified"] == 0
