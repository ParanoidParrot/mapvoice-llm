import json
from mapvoice_llm.source_readers import read_geojson_rows

def test_osm_geojson_language_name(tmp_path):
    path = tmp_path / "x.geojson"
    path.write_text(json.dumps({
        "type":"FeatureCollection",
        "features":[{
            "type":"Feature","id":"node/1",
            "geometry":{"type":"Point","coordinates":[80.2,13.0]},
            "properties":{"name":"Adyar","name:ta":"அடையாறு","place":"suburb","@id":"node/1"}
        }]
    }))
    rows = read_geojson_rows(path, language_code="ta")
    assert rows[0]["latin_name"] == "Adyar"
    assert rows[0]["native_name"] == "அடையாறு"
    assert rows[0]["source_record_id"] == "node/1"
