import json
from mapvoice_llm.training_profiles import TrainingProfileRegistry

def test_training_profile_registry(tmp_path):
    path=tmp_path/'profiles.json'
    path.write_text(json.dumps({"default_profile_id":"x","profiles":[{"profile_id":"x","label":"Test","description":"test","quantization":"none","epochs":2,"learning_rate":0.001,"batch_size":1,"gradient_accumulation_steps":4,"recommended_device":"cpu","notes":""}]}))
    registry=TrainingProfileRegistry(path)
    assert registry.default().profile_id=='x'
    assert registry.get('x').epochs==2
