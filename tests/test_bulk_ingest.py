
import csv
from pathlib import Path

from mapvoice_llm.bulk_ingest import ingest_rows
from mapvoice_llm.pack_context import PackContext
from mapvoice_llm.pack_schema import GENERIC_CANDIDATE_FIELDS, GENERIC_ENTITY_FIELDS
from mapvoice_llm.regional_packs import RegionalPack
from mapvoice_llm.source_registry import SourceDefinition


def test_bulk_ingest_dedupes_and_writes_manifest(tmp_path):
    entity_file = tmp_path / "entities.csv"
    with entity_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_ENTITY_FIELDS)
        writer.writeheader()

    candidate_file = tmp_path / "candidates.csv"
    with candidate_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GENERIC_CANDIDATE_FIELDS)
        writer.writeheader()

    source_file = tmp_path / "source.csv"
    source_file.write_text("name\nAdyar\nAdyar\n", encoding="utf-8")

    pack = RegionalPack(
        pack_id="chn-ta",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        region_language="Tamil",
        region_language_code="ta",
        navigation_languages=["English", "Tamil"],
        entity_file="entities.csv",
        candidate_file="candidates.csv",
        evaluation_suites=[],
    )
    context = PackContext(project_root=tmp_path, pack=pack)
    source = SourceDefinition(
        source_id="osm-test",
        label="OSM test",
        source_type="osm-extract",
        homepage="https://example.com",
        license="ODbL-1.0",
        attribution="© OpenStreetMap contributors",
        allowed_pack_ids=["chn-ta"],
        acquisition_mode="downloaded-file",
    )

    result = ingest_rows(
        project_root=tmp_path,
        context=context,
        source=source,
        input_path=source_file,
        rows=[
            {"name": "Adyar", "id": "1", "native_name": "அடையாறு"},
            {"name": "Adyar", "id": "2", "native_name": "அடையாறு"},
        ],
    )

    assert result["accepted"] == 1
    assert result["skipped_duplicate"] == 1
    assert (tmp_path / result["manifest"]).exists()
