from __future__ import annotations

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    text: str = Field(min_length=1)
    include_model: bool = False
    include_audio: bool = False


class DemoSample(BaseModel):
    id: str
    label: str
    text: str
    difficulty: str = "standard"


class ExperimentRequest(BaseModel):
    backend: str = Field(pattern="^(rule|model)$")
    suite_id: str = "entity-held-out"
    limit: int | None = Field(default=10, ge=1, le=500)


class CandidatePatchRequest(BaseModel):
    annotation_status: str | None = Field(
        default=None,
        pattern="^(candidate|reviewed|rejected)$",
    )
    kannada_name: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    notes: str | None = None


class ImprovementExportRequest(BaseModel):
    experiment_id: str = Field(min_length=1)
