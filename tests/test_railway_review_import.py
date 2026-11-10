import csv
import json
from pathlib import Path

from mapvoice_llm.railway_review_import import import_railway_reviews
from mapvoice_llm.review_store import ReviewStore


def _project(tmp_path: Path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "data" / "seeds").mkdir(parents=True)
    (tmp_path / "configs" / "regional_packs.json").write_text(json.dumps({
        "default_pack_id": "blr-kn",
        "packs": [{
            "pack_id":"blr-kn", "city":"Bengaluru", "state":"Karnataka", "country":"India",
            "region_language":"Kannada", "region_language_code":"kn", "navigation_languages":["English","Kannada"],
            "entity_file":"data/raw/x.csv", "candidate_file":"data/seeds/kn.csv", "evaluation_suites":[],
            "default_base_model":"x", "default_tts_language_code":"kn-IN", "status":"experimental", "description":"x"
        }]
    }), encoding="utf-8")
    with (tmp_path / "data" / "seeds" / "kn.csv").open("w", newline="", encoding="utf-8") as h:
        w=csv.DictWriter(h, fieldnames=["candidate_id","english_name","entity_type"]); w.writeheader();
        w.writerow({"candidate_id":"cand_0001","english_name":"Jayanagar","entity_type":"locality"})
        w.writerow({"candidate_id":"cand_0005","english_name":"Kengeri","entity_type":"locality"})


def _csv(path: Path):
    fields=["review_id","candidate_id","reviewer_id","language_code","latin_name","suggested_native_name","corrected_native_name","spelling_status","pronunciation_status","place_familiarity","notes","created_at"]
    rows=[
        ["r1","blr-kn-001","123","kn","Jayanagar","ಜಯನಗರ","","correct","correct","know","","2026-11-08T17:40:42+00:00"],
        ["r2","blr-kn-005","123","kn","Kengeri","ಕೆಂಗೇರಿ","","unsure","unsure","heard_of","","2026-11-08T17:41:18+00:00"],
    ]
    with path.open("w", newline="", encoding="utf-8") as h:
        w=csv.writer(h); w.writerow(fields); w.writerows(rows)


def test_import_maps_by_name_and_preserves_semantics(tmp_path):
    _project(tmp_path); f=tmp_path/"reviews.csv"; _csv(f)
    result=import_railway_reviews(project_root=tmp_path, review_csv=f)
    assert result.events_appended == 2
    events=ReviewStore(tmp_path,"blr-kn").list()
    assert events[0]["candidate_id"] == "cand_0001"
    assert events[0]["review_id"] == "r1"
    assert events[0]["decision"] == "approve"
    assert events[0]["pronunciation_approved"] is True
    assert events[1]["decision"] == "needs-correction"
    assert events[1]["spelling_status"] == "unsure"
    assert events[1]["pronunciation_approved"] is False


def test_reimport_is_idempotent_by_review_id(tmp_path):
    _project(tmp_path); f=tmp_path/"reviews.csv"; _csv(f)
    first=import_railway_reviews(project_root=tmp_path, review_csv=f)
    second=import_railway_reviews(project_root=tmp_path, review_csv=f)
    assert first.events_appended == 2
    assert second.events_appended == 0
    assert second.duplicate_review_id == 2
    assert len(ReviewStore(tmp_path,"blr-kn").list()) == 2
