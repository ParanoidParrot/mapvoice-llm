from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from mapvoice_llm.adapter_registry import AdapterRegistry
from mapvoice_llm.hf_export import adapter_manifest, write_export_bundle
from mapvoice_llm.regional_packs import RegionalPackRegistry


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('adapter_id')
    parser.add_argument('--pack-id', default='blr-kn')
    parser.add_argument('--output-dir')
    parser.add_argument('--license', default='other')
    parser.add_argument('--project-url')
    return parser.parse_args()


def main():
    args = parse_args()
    adapter = AdapterRegistry(PROJECT_ROOT / 'configs' / 'adapter_registry.json').get(args.adapter_id)
    if adapter is None:
        raise SystemExit(f'Adapter not found: {args.adapter_id}')
    pack = RegionalPackRegistry(PROJECT_ROOT / 'configs' / 'regional_packs.json').get(args.pack_id).to_dict()
    output_dir = Path(args.output_dir) if args.output_dir else PROJECT_ROOT / 'outputs' / 'hf_exports' / args.adapter_id
    manifest = adapter_manifest(adapter=adapter, pack=pack, license_name=args.license)
    write_export_bundle(output_dir=output_dir, manifest=manifest, project_url=args.project_url)
    print(json.dumps({
        'adapter_id': args.adapter_id,
        'pack_id': args.pack_id,
        'output_dir': str(output_dir),
        'files': [str(output_dir / 'mapvoice_manifest.json'), str(output_dir / 'README.md')],
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
