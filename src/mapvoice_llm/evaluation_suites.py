from __future__ import annotations

import csv
import json
from pathlib import Path


class EvaluationSuiteRegistry:
    def __init__(self, project_root: str | Path):
        self.root = Path(project_root)

    def list(self) -> list[dict]:
        return [
            {
                "id": "entity-held-out",
                "label": "Entity-held-out",
                "description": "Processed test split with entities held out from training.",
                "kind": "training-jsonl",
                "path": "data/processed/test.jsonl",
            },
            {
                "id": "lexicon-known",
                "label": "Lexicon-known",
                "description": "Known entities that should be solved well by the hybrid lookup path.",
                "kind": "evaluation-jsonl",
                "path": "data/evaluation/lexicon_known.jsonl",
            },
            {
                "id": "morphological-hard",
                "label": "Morphological hard",
                "description": "Hand-curated difficult Bengaluru names.",
                "kind": "evaluation-jsonl",
                "path": "data/evaluation/morphological_hard.jsonl",
            },
            {
                "id": "generated-hard-holdout",
                "label": "Generated hard holdout",
                "description": "Deterministically sampled suffix/non-suffix candidate holdout.",
                "kind": "evaluation-jsonl",
                "path": "data/evaluation/generated_hard_holdout.jsonl",
            },
        ]

    def get(self, suite_id: str) -> dict:
        for suite in self.list():
            if suite["id"] == suite_id:
                result = dict(suite)
                result["absolute_path"] = str(self.root / suite["path"])
                return result
        raise KeyError(suite_id)


def read_evaluation_jsonl(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []

    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]
