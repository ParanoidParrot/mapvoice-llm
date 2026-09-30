import json
from mapvoice_llm.training_preflight import run_training_preflight

def test_preflight_reports_environment_and_files(tmp_path):
    train=tmp_path/'train.jsonl'; validation=tmp_path/'validation.jsonl'
    record={
        'input': {'city':'Bengaluru','region_language':'Kannada','navigation_language':'English','text':'Continue towards Jayanagar.'},
        'target': {'place_name':'Jayanagar','place_name_kn':'ಜಯನಗರ','entity_type':'locality','language_origin':'Kannada','spoken_form':'ಜಯನಗರ','phonetic_form':None,'pronunciation_representation':'native-script'},
    }
    line=json.dumps(record,ensure_ascii=False)+'\n'
    train.write_text(line,encoding='utf-8'); validation.write_text(line,encoding='utf-8')
    report=run_training_preflight(train_file=train,validation_file=validation)
    assert 'runtime' in report and 'environment' in report
    if report['runtime']['ok']:
        assert report['files']['train_examples']==1
        assert report['files']['validation_examples']==1
