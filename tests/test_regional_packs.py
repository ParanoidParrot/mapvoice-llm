import json
from mapvoice_llm.regional_packs import RegionalPackRegistry


def test_registry_loads_default(tmp_path):
    path = tmp_path / 'packs.json'
    path.write_text(json.dumps({
        'default_pack_id': 'x-y',
        'packs': [{
            'pack_id': 'x-y','city': 'City','state': 'State','country': 'India',
            'region_language': 'Lang','region_language_code': 'xy',
            'navigation_languages': ['English','Lang'],'entity_file': 'data/raw/x.csv',
            'candidate_file': None,'evaluation_suites': [],'default_base_model': None,
            'default_tts_language_code': None,'status': 'experimental','description': 'test'
        }]
    }), encoding='utf-8')
    registry = RegionalPackRegistry(path)
    assert registry.default().pack_id == 'x-y'
    assert registry.get('x-y').region_language == 'Lang'
