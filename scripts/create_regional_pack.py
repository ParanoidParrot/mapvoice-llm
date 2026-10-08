from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.pack_schema import (
    GENERIC_CANDIDATE_FIELDS,
    GENERIC_ENTITY_FIELDS,
)
REGISTRY_FILE = PROJECT_ROOT / 'configs' / 'regional_packs.json'

ENTITY_FIELDS = [
    'entity_id','english_name','kannada_name','entity_type','city','language',
    'alternate_spellings','morphemes','suffix','verification_status',
    'pronunciation_verified','source_name','source_url','source_type','reviewer','notes'
]
CANDIDATE_FIELDS = [
    'candidate_id','english_name','entity_type','city','region_language',
    'annotation_status','kannada_name','source_name','source_url','notes'
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-id', required=True)
    parser.add_argument('--city', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--language-code', required=True)
    parser.add_argument('--tts-language-code')
    parser.add_argument('--base-model')
    return parser.parse_args()


def write_empty_csv(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()


def main():
    args = parse_args()
    data = json.loads(REGISTRY_FILE.read_text(encoding='utf-8'))
    if any(row['pack_id'] == args.pack_id for row in data['packs']):
        raise SystemExit(f'Pack already exists: {args.pack_id}')
    slug = args.pack_id.replace('-', '_')
    entity_file = f'data/raw/{slug}_entities.csv'
    candidate_file = f'data/seeds/{slug}_candidates.csv'
    write_empty_csv(PROJECT_ROOT / entity_file, GENERIC_ENTITY_FIELDS)
    write_empty_csv(PROJECT_ROOT / candidate_file, GENERIC_CANDIDATE_FIELDS)
    pack = {
        'pack_id': args.pack_id,
        'city': args.city,
        'state': args.state,
        'country': 'India',
        'region_language': args.language,
        'region_language_code': args.language_code,
        'navigation_languages': ['English', args.language],
        'entity_file': entity_file,
        'candidate_file': candidate_file,
        'evaluation_suites': ['entity-held-out','lexicon-known','morphological-hard','generated-hard-holdout'],
        'default_base_model': args.base_model,
        'default_tts_language_code': args.tts_language_code,
        'status': 'scaffold',
        'description': f'{args.city}-{args.language} navigation-language adaptation pack.',
    }
    data['packs'].append(pack)
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(pack, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
