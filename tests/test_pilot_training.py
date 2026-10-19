from mapvoice_llm.pilot_profiles import PilotProfile
from mapvoice_llm.pilot_training import build_pilot_training_plan
from mapvoice_llm.regional_packs import RegionalPack
from mapvoice_llm.training_profiles import TrainingProfile


def test_pilot_training_plan_refuses_unready_pack(tmp_path):
    pack = RegionalPack(
        pack_id="chn-ta",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        region_language="Tamil",
        region_language_code="ta",
        navigation_languages=["English", "Tamil"],
        entity_file="data/raw/chn_ta_entities.csv",
        candidate_file=None,
        evaluation_suites=[],
    )

    pilot = PilotProfile(
        pack_id="chn-ta",
        minimum_verified_entities=12,
        train_entities=8,
        validation_entities=2,
        test_entities=2,
    )

    training = TrainingProfile(
        profile_id="local-mac",
        label="Local",
        description="",
        quantization="none",
        epochs=3,
        learning_rate=0.0002,
        batch_size=1,
        gradient_accumulation_steps=8,
        recommended_device="mps",
    )

    result = build_pilot_training_plan(
        project_root=tmp_path,
        pack=pack,
        pilot_profile=pilot,
        training_profile=training,
        model_name="sarvamai/sarvam-1",
    )

    assert not result["plan_ready"]
    assert not result["ready"]
