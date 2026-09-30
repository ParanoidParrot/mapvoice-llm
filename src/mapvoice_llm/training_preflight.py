from __future__ import annotations

import json
from pathlib import Path

from .prompts import format_sft_example
from .runtime_compat import environment_snapshot, python_runtime_check

def _read_jsonl(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]

def run_training_preflight(*, train_file: str | Path, validation_file: str | Path, dataset_smoke_limit: int = 2) -> dict:
    runtime = python_runtime_check()
    report = {
        'runtime': {'ok': runtime.ok, 'level': runtime.level, 'message': runtime.message},
        'environment': environment_snapshot(),
        'files': {},
        'dataset_smoke_test': {'ok': False, 'message': 'not run'},
    }
    if not runtime.ok:
        return report

    train_rows = _read_jsonl(train_file)
    validation_rows = _read_jsonl(validation_file)
    report['files'] = {
        'train_file': str(train_file), 'train_examples': len(train_rows),
        'validation_file': str(validation_file), 'validation_examples': len(validation_rows),
    }
    if not train_rows:
        report['dataset_smoke_test'] = {'ok': False, 'message': 'Training dataset is empty.'}
        return report
    if not validation_rows:
        report['dataset_smoke_test'] = {'ok': False, 'message': 'Validation dataset is empty.'}
        return report

    formatted = [format_sft_example(row) for row in train_rows[:dataset_smoke_limit]]
    try:
        from datasets import Dataset
        dataset = Dataset.from_list(formatted)
        report['dataset_smoke_test'] = {
            'ok': True,
            'message': f'Hugging Face Dataset.from_list succeeded for {len(dataset)} sample rows.',
        }
    except Exception as exc:
        report['dataset_smoke_test'] = {
            'ok': False,
            'message': (
                'Hugging Face Dataset construction failed before training. '
                f'{type(exc).__name__}: {exc}'
            ),
        }
    return report

def preflight_ok(report: dict) -> bool:
    return bool(report.get('runtime',{}).get('ok') and report.get('dataset_smoke_test',{}).get('ok'))
