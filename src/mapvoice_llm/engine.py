from __future__ import annotations

from pathlib import Path

from .baseline import RuleBaseline
from .model_backend import TransformersBackend
from .normalization import normalize_navigation_text
from .schemas import PronunciationResult


class MapVoiceEngine:
    def __init__(
        self,
        entity_csv: str | Path,
        model_name: str | None = None,
        adapter_path: str | None = None,
    ):
        self.baseline = RuleBaseline(entity_csv)
        self.model_name = model_name
        self.adapter_path = adapter_path
        self._model_backend: TransformersBackend | None = None

    def _get_model(self) -> TransformersBackend:
        if not self.model_name:
            raise RuntimeError("No model_name configured for transformer inference")

        if self._model_backend is None:
            self._model_backend = TransformersBackend(
                model_name=self.model_name,
                adapter_path=self.adapter_path,
            )
        return self._model_backend

    def predict_rule(self, text: str) -> PronunciationResult:
        return self.baseline.predict(text)

    def predict_model(self, text: str) -> PronunciationResult:
        parsed = self._get_model().generate(text)

        if not parsed.valid_json or not parsed.data:
            fallback = self.baseline.predict(text)
            fallback.source = "rule-fallback-after-invalid-model-output"
            return fallback

        data = parsed.data
        spoken_form = data.get("spoken_form") or data.get("pronunciation_form")

        return PronunciationResult(
            original_text=text,
            normalized_instruction=normalize_navigation_text(text),
            detected_entity=data.get("place_name"),
            entity_kannada=data.get("place_name_kn"),
            entity_type=data.get("entity_type"),
            spoken_form=spoken_form,
            phonetic_form=data.get("phonetic_form"),
            pronunciation_representation=data.get("pronunciation_representation"),
            pronunciation_form=spoken_form,
            source="adapter-model" if self.adapter_path else "base-model",
        )

    def predict(self, text: str, backend: str = "rule") -> PronunciationResult:
        if backend == "rule":
            return self.predict_rule(text)
        if backend == "model":
            return self.predict_model(text)
        raise ValueError(f"Unsupported backend: {backend}")
