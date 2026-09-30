from __future__ import annotations
import argparse, json, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))
from mapvoice_llm.training_preflight import preflight_ok, run_training_preflight

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--train-file', default=str(PROJECT_ROOT/'data/processed/train.jsonl'))
    p.add_argument('--validation-file', default=str(PROJECT_ROOT/'data/processed/validation.jsonl'))
    args=p.parse_args()
    report=run_training_preflight(train_file=args.train_file, validation_file=args.validation_file)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not preflight_ok(report): raise SystemExit(1)
if __name__=='__main__': main()
