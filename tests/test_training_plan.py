from mapvoice_llm.regional_packs import RegionalPack
from mapvoice_llm.training_plan import build_training_plan
from mapvoice_llm.training_profiles import TrainingProfile

def test_training_plan_uses_pack_paths(tmp_path):
    pack=RegionalPack(pack_id='blr-kn',city='Bengaluru',state='Karnataka',country='India',region_language='Kannada',region_language_code='kn',navigation_languages=['English','Kannada'],entity_file='data/raw/entities.csv',candidate_file=None,evaluation_suites=[],default_base_model='base/model')
    profile=TrainingProfile(profile_id='local',label='Local',description='',quantization='none',epochs=3,learning_rate=.0002,batch_size=1,gradient_accumulation_steps=8,recommended_device='mps')
    plan=build_training_plan(project_root=tmp_path,pack=pack,profile=profile,version='v2')
    assert plan.adapter_id=='mapvoice-blr-kn-v2'
    assert 'data/processed/packs/blr-kn/train.jsonl' in plan.command
    assert '--register-adapter' in plan.command
