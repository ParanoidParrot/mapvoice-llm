from mapvoice_llm.pack_evaluation import build_pack_evaluation
from mapvoice_llm.regional_entity import RegionalEntity
from mapvoice_llm.regional_packs import RegionalPack


def test_empty_pack_evaluation_is_explicit(tmp_path):
    pack = RegionalPack(
        pack_id="x-ml",
        city="City",
        state="State",
        country="India",
        region_language="Malayalam",
        region_language_code="ml",
        navigation_languages=["English", "Malayalam"],
        entity_file="entities.csv",
        candidate_file=None,
        evaluation_suites=[],
    )

    result = build_pack_evaluation(
        project_root=tmp_path,
        pack=pack,
        entities=[],
    )

    assert result["labeled_entities"] == 0
    assert result["status"] == "empty-until-labels-reviewed"
