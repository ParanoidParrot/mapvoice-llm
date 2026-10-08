from pathlib import Path

from mapvoice_llm.regional_pack_status import regional_pack_status
from mapvoice_llm.regional_packs import RegionalPackRegistry


def test_repository_has_parallel_packs():
    root = Path(__file__).resolve().parents[1]

    registry = RegionalPackRegistry(
        root / "configs/regional_packs.json"
    )

    ids = {
        item.pack_id
        for item in registry.list()
    }

    assert {
        "blr-kn",
        "chn-ta",
        "hyd-te",
        "mum-mr",
        "kochi-ml",
    }.issubset(ids)

    rows = regional_pack_status(
        project_root=root,
        registry=registry,
    )

    by_id = {
        row["pack_id"]: row
        for row in rows
    }

    assert by_id["chn-ta"]["candidate_count"] == 20
    assert by_id["hyd-te"]["candidate_count"] == 20
    assert by_id["mum-mr"]["candidate_count"] == 20
    assert by_id["kochi-ml"]["candidate_count"] == 20
