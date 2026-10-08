import csv
from mapvoice_llm.entity_repository import RegionalEntityRepository
from mapvoice_llm.pack_dataset import build_pack_dataset
from mapvoice_llm.pack_schema import GENERIC_ENTITY_FIELDS
from mapvoice_llm.regional_packs import RegionalPack

def test_pack_dataset_is_entity_split(tmp_path):
    entities=tmp_path/'entities.csv'
    with entities.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=GENERIC_ENTITY_FIELDS);writer.writeheader()
        for i in range(6):
            writer.writerow({"entity_id":f"e{i}","latin_name":f"Place {i}","native_name":f"Native {i}","entity_type":"locality","city":"City","language":"Language","language_code":"xx","alternate_spellings":"","morphemes":"","suffix":"","verification_status":"reviewed","pronunciation_verified":"false","source_name":"","source_url":"","source_type":"","reviewer":"","notes":""})
    pack=RegionalPack(pack_id='x-y',city='City',state='State',country='India',region_language='Language',region_language_code='xx',navigation_languages=['English','Language'],entity_file=str(entities),candidate_file=None,evaluation_suites=[])
    result=build_pack_dataset(project_root=tmp_path,pack=pack,entity_repository=RegionalEntityRepository(entities))
    assert result.total_examples==48
    assert sum(result.split_entities.values())==6
    assert (tmp_path/'data/processed/packs/x-y/manifest.json').exists()
