import csv
from mapvoice_llm.review_queue import build_review_queue

def test_review_queue_prefers_native_and_provenance(tmp_path):
    path = tmp_path / "c.csv"
    fields = ["candidate_id","latin_name","annotation_status","native_name","source_id",
              "source_license","source_record_id","source_url","source_snapshot_sha256",
              "latitude","longitude"]
    with path.open("w", newline="", encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader()
        w.writerow({"candidate_id":"1","latin_name":"A","annotation_status":"candidate","native_name":""})
        w.writerow({"candidate_id":"2","latin_name":"B","annotation_status":"candidate","native_name":"ந","source_id":"s","source_license":"ODbL-1.0","source_record_id":"x","source_url":"u","source_snapshot_sha256":"h","latitude":"1","longitude":"2"})
    rows = build_review_queue(path)
    assert rows[0]["candidate_id"] == "2"
