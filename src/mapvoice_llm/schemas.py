from pydantic import BaseModel, Field


class NormalizeRequest(BaseModel):
    text: str = Field(min_length=1)
    city: str = "Bengaluru"
    region_language: str = "Kannada"
    navigation_language: str = "English"
    backend: str = Field(default="rule", pattern="^(rule|model)$")


class PronunciationResult(BaseModel):
    original_text: str
    normalized_instruction: str
    detected_entity: str | None = None
    entity_kannada: str | None = None
    entity_type: str | None = None

    # v0.3 fields
    spoken_form: str | None = None
    phonetic_form: str | None = None
    pronunciation_representation: str | None = None

    # Backward-compatible alias used by v0.1/v0.2 scripts.
    pronunciation_form: str | None = None

    source: str = "rule-baseline"


class ModelStatus(BaseModel):
    configured: bool
    model_name: str | None = None
    adapter_path: str | None = None
