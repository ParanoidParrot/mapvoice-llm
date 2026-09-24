"""
Model inference abstraction.

v0.1 keeps the deterministic baseline runnable immediately.
The transformer/adapter path can be enabled after the first LoRA artifact exists.
"""

from pathlib import Path
from .baseline import RuleBaseline
from .schemas import PronunciationResult


class MapVoiceInference:
    def __init__(self, entity_csv: str | Path):
        self.baseline = RuleBaseline(entity_csv)

    def predict(self, text: str) -> PronunciationResult:
        # TODO:
        # 1. query exact geographic lexicon
        # 2. if unknown, call fine-tuned model
        # 3. validate structured output
        # 4. assign confidence
        # 5. fall back to rule baseline when required
        return self.baseline.predict(text)
