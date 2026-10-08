from __future__ import annotations

import json
from pathlib import Path


def adapter_manifest(*, adapter: dict, pack: dict, metrics: dict | None = None, license_name: str | None = None) -> dict:
    return {
        'format_version': 1,
        'artifact_type': 'peft-adapter',
        'adapter_id': adapter.get('adapter_id'),
        'adapter_path': adapter.get('adapter_path'),
        'base_model': adapter.get('base_model'),
        'training_run_id': adapter.get('training_run_id'),
        'regional_pack': {
            'pack_id': pack.get('pack_id'),
            'city': pack.get('city'),
            'state': pack.get('state'),
            'country': pack.get('country'),
            'region_language': pack.get('region_language'),
            'region_language_code': pack.get('region_language_code'),
            'navigation_languages': pack.get('navigation_languages'),
        },
        'metrics': metrics or {},
        'license': license_name,
    }


def render_model_card(*, manifest: dict, project_url: str | None = None) -> str:
    region = manifest.get('regional_pack') or {}
    metrics = manifest.get('metrics') or {}
    lines = [
        '---',
        f"base_model: {manifest.get('base_model') or 'unknown'}",
        'library_name: peft',
        'pipeline_tag: text-generation',
        f"license: {manifest.get('license') or 'other'}",
        'tags:',
        '  - mapvoice',
        '  - navigation',
        '  - indic-languages',
        f"  - {region.get('region_language_code') or 'regional-language'}",
        '---',
        '',
        f"# {manifest.get('adapter_id') or 'MapVoice Regional Adapter'}",
        '',
        'Experimental MapVoice regional navigation-language adapter.',
        '',
        '## Regional scope',
        '',
        f"- City: {region.get('city') or 'unknown'}",
        f"- State/region: {region.get('state') or 'unknown'}",
        f"- Country: {region.get('country') or 'unknown'}",
        f"- Regional language: {region.get('region_language') or 'unknown'}",
        f"- Navigation languages: {', '.join(region.get('navigation_languages') or []) or 'unknown'}",
        '',
        '## Base model',
        '',
        f"`{manifest.get('base_model') or 'unknown'}`",
        '',
        '## Task',
        '',
        'Convert navigation text into a structured local-place representation with native-script/spoken-form targets suitable for downstream pronunciation/TTS.',
        '',
        '## Training artifact',
        '',
        f"- Adapter ID: `{manifest.get('adapter_id') or 'unknown'}`",
        f"- Training run: `{manifest.get('training_run_id') or 'unknown'}`",
        '',
        '## Evaluation',
        '',
    ]
    if metrics:
        for key, value in metrics.items():
            lines.append(f'- {key}: {value}')
    else:
        lines.append('No evaluation metrics have been attached to this export yet. Do not interpret this artifact as validated for production use.')
    lines += [
        '',
        '## Intended use',
        '',
        'Research and experimentation on geographically specialized navigation-language adaptation.',
        '',
        '## Limitations',
        '',
        '- Geographic coverage is limited to the stated regional pack.',
        '- Place-name labels require human/native-language verification.',
        '- Evaluation should include unseen entities and morphology-heavy names.',
        '- This adapter should not be treated as a general-purpose language model.',
        '',
        '## License',
        '',
        f"Adapter metadata declares `{manifest.get('license') or 'unspecified'}`. The base-model license and any dataset/source licenses also apply.",
    ]
    if project_url:
        lines += ['', '## Project', '', project_url]
    return '\n'.join(lines) + '\n'


def write_export_bundle(*, output_dir: str | Path, manifest: dict, project_url: str | None = None) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'mapvoice_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (output_dir / 'README.md').write_text(render_model_card(manifest=manifest, project_url=project_url), encoding='utf-8')
    return output_dir
