from __future__ import annotations

import time
import importlib.util
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .audio_store import AudioStore
from .adapter_registry import AdapterRegistry
from .checkpoints import discover_checkpoints
from .runtime_models import RuntimeModelManager
from .regional_packs import RegionalPackRegistry
from .regional_pack_status import regional_pack_status
from .pack_context import load_pack_context
from .training_runs import TrainingRunStore
from .training_profiles import TrainingProfileRegistry
from .training_plan import build_training_plan
from .data_quality import POLICIES
from .language_profiles import LanguageProfileRegistry
from .language_validation import audit_entities
from .source_registry import SourceRegistry
from .base_model_registry import BaseModelRegistry
from .kannada_adapter_pipeline import lifecycle_status
from .provenance import score_candidate
from .pack_dataset import build_pack_dataset
from .experiment_compare import compare_experiments
from .candidates import CandidateRepository, CandidateUpdate
from .config import settings
from .demo_data import samples_for_pack
from .demo_runs import DemoRunStore
from .engine import MapVoiceEngine
from .evaluation_suites import EvaluationSuiteRegistry
from .evaluator import evaluate_model, evaluate_rule
from .suite_evaluator import evaluate_suite_model, evaluate_suite_rule
from .experiment_store import ExperimentStore
from .schemas import ModelStatus, NormalizeRequest, PronunciationResult
from .status import dataset_status
from .readiness import training_readiness
from .tts import build_tts_provider
from .project_status import project_status
from .improvement_dataset import build_improvement_rows, write_jsonl as write_improvement_jsonl
from .web_schemas import (
    AdapterPromoteRequest,
    AdapterRegisterRequest,
    CandidatePatchRequest,
    CompareRequest,
    ExperimentRequest,
    ImprovementExportRequest,
    ModelCompareRequest,
    TrainingPlanRequest,
    ExperimentCompareRequest,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENTITY_CSV = PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.4.csv"
FALLBACK_ENTITY_CSV = (
    PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
)
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "test.jsonl"
CANDIDATE_CSV = (
    PROJECT_ROOT / "data" / "seeds" / "bengaluru_candidates_v0.6.csv"
)

UI_DIR = PROJECT_ROOT / "ui"
AUDIO_DIR = PROJECT_ROOT / "outputs" / "generated_audio"
RUN_DIR = PROJECT_ROOT / "outputs" / "demo_runs"
EXPERIMENT_DIR = PROJECT_ROOT / "outputs" / "experiments"
TRAINING_RUN_DIR = PROJECT_ROOT / "outputs" / "training_runs"
ADAPTER_REGISTRY_FILE = PROJECT_ROOT / "configs" / "adapter_registry.json"
REGIONAL_PACK_REGISTRY_FILE = PROJECT_ROOT / "configs" / "regional_packs.json"
TRAINING_PROFILE_FILE = PROJECT_ROOT / "configs" / "training_profiles.json"
LANGUAGE_PROFILE_FILE = PROJECT_ROOT / "configs" / "language_profiles.json"
SOURCE_REGISTRY_FILE = PROJECT_ROOT / "configs" / "source_registry.json"
BASE_MODEL_REGISTRY_FILE = PROJECT_ROOT / "configs" / "base_models.json"
ARTIFACT_ROOT = PROJECT_ROOT / "artifacts"
IMPROVEMENT_DIR = PROJECT_ROOT / "outputs" / "improvement_datasets"


app = FastAPI(
    title="MapVoice-LLM",
    version="1.9.0",
    description="Regional navigation-language adaptation experiments for MapVoice",
)

regional_pack_registry = RegionalPackRegistry(REGIONAL_PACK_REGISTRY_FILE)
training_profile_registry = TrainingProfileRegistry(TRAINING_PROFILE_FILE)
language_profile_registry = LanguageProfileRegistry(LANGUAGE_PROFILE_FILE)
source_registry = SourceRegistry(SOURCE_REGISTRY_FILE)
base_model_registry = BaseModelRegistry(BASE_MODEL_REGISTRY_FILE)
active_pack_context = load_pack_context(PROJECT_ROOT, settings.pack_id)

ACTIVE_ENTITY_CSV = active_pack_context.entity_csv
if not ACTIVE_ENTITY_CSV.exists():
    ACTIVE_ENTITY_CSV = (
        ENTITY_CSV if ENTITY_CSV.exists() else FALLBACK_ENTITY_CSV
    )

ACTIVE_CANDIDATE_CSV = (
    active_pack_context.candidate_csv or CANDIDATE_CSV
)

adapter_registry = AdapterRegistry(ADAPTER_REGISTRY_FILE)
runtime_models = RuntimeModelManager(
    entity_csv=ACTIVE_ENTITY_CSV,
    base_model_name=settings.model_name,
    default_adapter_path=settings.adapter_path,
    adapter_registry=adapter_registry,
)
engine = runtime_models.base_engine

tts = build_tts_provider(
    settings,
    default_language_code=(
        active_pack_context.pack.default_tts_language_code
        or settings.sarvam_tts_target_language
    ),
)
audio_store = AudioStore(AUDIO_DIR)
run_store = DemoRunStore(RUN_DIR)
experiment_store = ExperimentStore(EXPERIMENT_DIR)
training_run_store = TrainingRunStore(TRAINING_RUN_DIR)
candidate_repo = CandidateRepository(ACTIVE_CANDIDATE_CSV)
suite_registry = EvaluationSuiteRegistry(PROJECT_ROOT)

if (UI_DIR / "static").exists():
    app.mount(
        "/static",
        StaticFiles(directory=UI_DIR / "static"),
        name="static",
    )

app.mount(
    "/audio",
    StaticFiles(directory=AUDIO_DIR),
    name="audio",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    index = UI_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>MapVoice-LLM</h1><p>UI not found.</p>")
    return HTMLResponse(index.read_text(encoding="utf-8"))


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo() -> HTMLResponse:
    return home()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "project": "mapvoice-llm",
        "version": "1.9.0",
        "regional_pack": active_pack_context.pack.pack_id,
    }



@app.get("/project/status")
def get_project_status() -> dict:
    tts_snapshot = {
        "enabled": settings.tts_enabled,
        "provider": settings.tts_provider,
        "available": bool(getattr(tts, "available", False)),
    }

    return project_status(
        project_root=PROJECT_ROOT,
        active_pack=active_pack_context.pack.to_dict(),
        active_entity_csv=ACTIVE_ENTITY_CSV,
        active_candidate_csv=ACTIVE_CANDIDATE_CSV,
        adapter_registry=adapter_registry,
        training_run_store=training_run_store,
        tts_status=tts_snapshot,
        model_name=settings.model_name,
    )


@app.get("/model/status")
def model_status() -> dict:
    active = adapter_registry.active()
    return {
        "configured": bool(settings.model_name),
        "model_name": settings.model_name,
        "env_adapter_path": settings.adapter_path,
        "active_adapter": active,
        "registered_adapters": len(adapter_registry.list()),
    }



@app.get("/regional-packs/active")
def get_active_regional_pack() -> dict:
    return active_pack_context.pack.to_dict()


@app.get("/regional-packs/status")
def get_regional_pack_status() -> dict:
    return {
        "packs": regional_pack_status(
            project_root=PROJECT_ROOT,
            registry=regional_pack_registry,
        )
    }


@app.get("/regional-packs")
def list_regional_packs() -> dict:
    return {
        "default_pack": regional_pack_registry.default().to_dict(),
        "packs": [pack.to_dict() for pack in regional_pack_registry.list()],
    }


@app.get("/regional-packs/{pack_id}")
def get_regional_pack(pack_id: str) -> dict:
    try:
        return regional_pack_registry.get(pack_id).to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail="Regional pack not found")


@app.get("/adapters")
def list_adapters() -> dict:
    return {
        "active_adapter": adapter_registry.active(),
        "adapters": adapter_registry.list(),
    }


@app.post("/adapters/register")
def register_adapter(request: AdapterRegisterRequest) -> dict:
    adapter_path = Path(request.adapter_path)

    if not adapter_path.is_absolute():
        adapter_path = PROJECT_ROOT / adapter_path

    record = adapter_registry.register({
        "adapter_id": request.adapter_id,
        "adapter_path": str(adapter_path),
        "base_model": request.base_model,
        "training_run_id": request.training_run_id,
        "notes": request.notes,
    })

    runtime_models.clear_cache()
    return record


@app.post("/adapters/promote")
def promote_adapter(request: AdapterPromoteRequest) -> dict:
    try:
        record = adapter_registry.promote(request.adapter_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Adapter not found")

    runtime_models.clear_cache()
    return {"active_adapter": record}


@app.post("/adapters/clear-active")
def clear_active_adapter() -> dict:
    adapter_registry.clear_active()
    runtime_models.clear_cache()
    return {"active_adapter": None}





@app.get("/base-models")
def list_base_models() -> dict:
    return {
        "reference": base_model_registry.reference().to_dict(),
        "models": [
            model.to_dict()
            for model in base_model_registry.list()
        ],
    }


@app.get("/adapters/kannada-v1/status")
def kannada_adapter_v1_status() -> dict:
    return lifecycle_status(
        project_root=PROJECT_ROOT,
        adapter_id="mapvoice-blr-kn-v1",
    )


@app.get("/data-sources")
def list_data_sources() -> dict:
    return {
        "sources": [
            source.to_dict()
            for source in source_registry.list()
        ]
    }


@app.get("/regional-packs/{pack_id}/provenance-status")
def get_pack_provenance_status(pack_id: str) -> dict:
    try:
        context = load_pack_context(
            PROJECT_ROOT,
            pack_id,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Regional pack not found",
        )

    if context.candidate_csv is None or not context.candidate_csv.exists():
        return {
            "pack_id": pack_id,
            "candidates": 0,
            "complete": 0,
            "partial": 0,
            "insufficient": 0,
            "average_score": 0,
        }

    import csv

    with context.candidate_csv.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    scores = [
        score_candidate(row)
        for row in rows
    ]

    return {
        "pack_id": pack_id,
        "candidates": len(rows),
        "complete": sum(
            item.status == "complete"
            for item in scores
        ),
        "partial": sum(
            item.status == "partial"
            for item in scores
        ),
        "insufficient": sum(
            item.status == "insufficient"
            for item in scores
        ),
        "average_score": (
            round(
                sum(item.score for item in scores)
                / len(scores),
                2,
            )
            if scores
            else 0
        ),
    }


@app.get("/training/dataset-policies")
def list_dataset_policies() -> dict:
    return {
        "policies": [
            policy.to_dict()
            for policy in POLICIES.values()
        ]
    }


@app.get("/regional-packs/{pack_id}/label-audit")
def get_pack_label_audit(pack_id: str) -> dict:
    try:
        context = load_pack_context(
            PROJECT_ROOT,
            pack_id,
        )
        profile = language_profile_registry.get(
            context.pack.region_language_code
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Regional pack/language profile not found",
        )

    return {
        "pack_id": pack_id,
        **audit_entities(
            context.entity_repository.list(),
            profile,
        ),
    }


@app.get("/training/profiles")
def list_training_profiles() -> dict:
    return {"default_profile": training_profile_registry.default().to_dict(),
            "profiles": [profile.to_dict() for profile in training_profile_registry.list()]}


@app.post("/training/plan")
def create_training_plan(request: TrainingPlanRequest) -> dict:
    try:
        pack = regional_pack_registry.get(request.pack_id) if request.pack_id else active_pack_context.pack
    except KeyError:
        raise HTTPException(status_code=404, detail="Regional pack not found")
    try:
        profile = training_profile_registry.get(request.profile_id) if request.profile_id else training_profile_registry.default()
    except KeyError:
        raise HTTPException(status_code=404, detail="Training profile not found")
    return build_training_plan(project_root=PROJECT_ROOT, pack=pack, profile=profile,
                               version=request.version, model_name=request.model_name).to_dict()


@app.post("/training/build-pack-dataset")
def api_build_pack_dataset(
    pack_id: str | None = None,
    policy: str = "labeled",
) -> dict:
    try:
        context = load_pack_context(PROJECT_ROOT, pack_id or active_pack_context.pack.pack_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Regional pack not found")
    return build_pack_dataset(project_root=PROJECT_ROOT, pack=context.pack,
                              entity_repository=context.entity_repository).to_dict()


@app.get("/training/runs")
def list_training_runs(limit: int = 50) -> dict:
    limit = max(1, min(limit, 200))
    return {"runs": training_run_store.list(limit=limit)}


@app.get("/training/runs/{run_id}")
def get_training_run(run_id: str) -> dict:
    run = training_run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Training run not found")
    return run


@app.get("/checkpoints")
def list_checkpoints() -> dict:
    return {"checkpoints": discover_checkpoints(ARTIFACT_ROOT)}


@app.post("/models/compare")
def compare_models(request: ModelCompareRequest) -> dict:
    rows = []

    for adapter_id in request.adapter_ids:
        try:
            selected_engine = runtime_models.model_engine(adapter_id)
            prediction = selected_engine.predict_model(request.text)

            rows.append({
                "adapter_id": adapter_id,
                "prediction": prediction.model_dump(),
                "error": None,
            })
        except Exception as exc:
            rows.append({
                "adapter_id": adapter_id,
                "prediction": None,
                "error": str(exc),
            })

    return {
        "text": request.text,
        "results": rows,
    }


@app.get("/tts/status")
def tts_status() -> dict:
    reason = getattr(tts, "reason", None)
    native_language_code = (
        active_pack_context.pack.default_tts_language_code
        or settings.sarvam_tts_target_language
    )

    return {
        "enabled": settings.tts_enabled,
        "provider": settings.tts_provider,
        "available": bool(getattr(tts, "available", False)),
        "reason": reason,
        "api_key_configured": bool(settings.sarvam_api_key),
        "sdk_installed": (
            importlib.util.find_spec("sarvamai")
            is not None
        ),
        "model": (
            settings.sarvam_tts_model
            if settings.tts_provider == "sarvam"
            else None
        ),
        "speaker": (
            settings.sarvam_tts_speaker
            if settings.tts_provider == "sarvam"
            else None
        ),
        "english_language_code": (
            settings.tts_english_language
        ),
        "native_language_code": native_language_code,
        "regional_pack": (
            active_pack_context.pack.pack_id
        ),
    }


@app.get("/demo/samples")
def demo_samples() -> dict:
    return {
        "regional_pack": active_pack_context.pack.pack_id,
        "samples": samples_for_pack(
            pack_id=active_pack_context.pack.pack_id,
            candidate_repository=candidate_repo,
        ),
    }


@app.get("/dataset/status")
def get_dataset_status() -> dict:
    status = dataset_status(ACTIVE_ENTITY_CSV)
    if ACTIVE_CANDIDATE_CSV.exists():
        status["candidates"] = candidate_repo.stats()
    return status


@app.get("/demo/runs")
def list_demo_runs(limit: int = 20) -> dict:
    limit = max(1, min(limit, 100))
    return {"runs": run_store.list(limit=limit)}


@app.get("/demo/runs/{run_id}")
def get_demo_run(run_id: str) -> dict:
    run = run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/experiments")
def list_experiments(limit: int = 20) -> dict:
    limit = max(1, min(limit, 100))
    return {"experiments": experiment_store.list(limit=limit)}


@app.post("/experiments/compare")
def compare_saved_experiments(request: ExperimentCompareRequest) -> dict:
    first = experiment_store.get(request.first_experiment_id)
    second = experiment_store.get(request.second_experiment_id)
    if first is None:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {request.first_experiment_id}")
    if second is None:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {request.second_experiment_id}")
    return compare_experiments(first, second)


@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: str) -> dict:
    result = experiment_store.get(experiment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@app.post("/experiments/export-improvement")
def export_improvement_dataset(
    request: ImprovementExportRequest,
) -> dict:
    experiment = experiment_store.get(request.experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    rows = build_improvement_rows(experiment)
    output = IMPROVEMENT_DIR / f"{request.experiment_id}_failures.jsonl"
    write_improvement_jsonl(rows, output)

    return {
        "experiment_id": request.experiment_id,
        "rows": len(rows),
        "output": str(output.relative_to(PROJECT_ROOT)),
    }


@app.get("/evaluation/suites")
def evaluation_suites() -> dict:
    return {"suites": suite_registry.list()}


@app.get("/training/readiness")
def get_training_readiness() -> dict:
    return training_readiness(
        ACTIVE_ENTITY_CSV,
        ACTIVE_CANDIDATE_CSV,
    )


@app.post("/experiments/evaluate")
def run_experiment(request: ExperimentRequest) -> dict:
    try:
        suite = suite_registry.get(request.suite_id)
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown evaluation suite: {request.suite_id}",
        )

    if request.backend == "rule":
        report = evaluate_suite_rule(
            entity_csv=ACTIVE_ENTITY_CSV,
            suite_path=suite["absolute_path"],
            suite_kind=suite["kind"],
            limit=request.limit,
        )
    else:
        if not settings.model_name:
            raise HTTPException(
                status_code=400,
                detail="No model is configured",
            )

        try:
            report = evaluate_suite_model(
                model_name=settings.model_name,
                adapter_path=settings.adapter_path,
                suite_path=suite["absolute_path"],
                suite_kind=suite["kind"],
                limit=request.limit,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    report["suite_id"] = suite["id"]
    report["suite_label"] = suite["label"]
    stored = experiment_store.save(report)
    return stored


@app.get("/annotations/candidates")
def list_candidates(
    status: str | None = None,
    limit: int = 100,
) -> dict:
    limit = max(1, min(limit, 500))
    return {
        "candidates": candidate_repo.list(
            status=status,
            limit=limit,
        ),
        "stats": candidate_repo.stats(),
    }


@app.get("/annotations/candidates/{candidate_id}")
def get_candidate(candidate_id: str) -> dict:
    row = candidate_repo.get(candidate_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return row


@app.patch("/annotations/candidates/{candidate_id}")
def patch_candidate(
    candidate_id: str,
    request: CandidatePatchRequest,
) -> dict:
    try:
        updated = candidate_repo.update(
            candidate_id,
            CandidateUpdate(
                annotation_status=request.annotation_status,
                native_name=request.native_name,
                kannada_name=request.kannada_name,
                source_name=request.source_name,
                source_url=request.source_url,
                notes=request.notes,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if updated is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return updated


@app.post("/normalize", response_model=PronunciationResult)
def normalize(request: NormalizeRequest) -> PronunciationResult:
    try:
        return engine.predict(request.text, backend=request.backend)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _synthesize_audio(
    *,
    original_text: str,
    normalized_text: str,
    native_text: str | None,
) -> dict:
    native_language_code = (
        active_pack_context.pack.default_tts_language_code
        or settings.sarvam_tts_target_language
    )

    result = {
        "raw_audio_url": None,
        "normalized_audio_url": None,
        "native_audio_url": None,
        "status": "not-requested",
        "provider": getattr(tts, "name", "unknown"),
        "errors": [],
        "cache_hits": [],
        "generated": [],
        "language_codes": {
            "raw": settings.tts_english_language,
            "normalized": settings.tts_english_language,
            "native": native_language_code,
        },
    }

    if not getattr(tts, "available", False):
        result["status"] = "unavailable"
        result["errors"].append(
            getattr(
                tts,
                "reason",
                "TTS provider is not available/configured",
            )
        )
        return result

    result["status"] = "partial"

    targets = [
        (
            "raw",
            original_text,
            settings.tts_english_language,
            "raw_audio_url",
        ),
        (
            "normalized",
            normalized_text,
            settings.tts_english_language,
            "normalized_audio_url",
        ),
        (
            "native",
            native_text,
            native_language_code,
            "native_audio_url",
        ),
    ]

    succeeded = 0
    attempted = 0

    for (
        kind,
        text,
        language_code,
        response_key,
    ) in targets:
        if not text:
            continue

        attempted += 1

        cache_key = "|".join([
            getattr(tts, "name", "unknown"),
            settings.sarvam_tts_model,
            settings.sarvam_tts_speaker,
            language_code or "",
        ])

        cached = audio_store.existing(
            kind=kind,
            text=text,
            extension="wav",
            cache_key=cache_key,
        )

        if cached:
            result[response_key] = (
                audio_store.url_for(cached)
            )
            result["cache_hits"].append(kind)
            succeeded += 1
            continue

        try:
            generated = tts.synthesize(
                text,
                language_code=language_code,
            )
            path = audio_store.save(
                kind=kind,
                text=text,
                audio_bytes=generated.audio_bytes,
                extension=generated.extension,
                cache_key=cache_key,
            )
            result[response_key] = (
                audio_store.url_for(path)
            )
            result["generated"].append(kind)
            succeeded += 1
        except Exception as exc:
            result["errors"].append(
                f"{kind}: {exc}"
            )

    if attempted and succeeded == attempted:
        result["status"] = "ready"
    elif succeeded == 0:
        result["status"] = "failed"

    return result


@app.post("/demo/compare")
def compare(request: CompareRequest) -> dict:
    started = time.perf_counter()

    rule_started = time.perf_counter()
    rule = engine.predict_rule(request.text)
    rule_ms = round((time.perf_counter() - rule_started) * 1000, 2)

    model_result = None
    model_error = None
    model_ms = None

    if request.include_model:
        model_started = time.perf_counter()
        try:
            selected_engine = runtime_models.model_engine(request.adapter_id)
            model_result = selected_engine.predict_model(request.text)
        except Exception as exc:
            model_error = str(exc)
        finally:
            model_ms = round(
                (time.perf_counter() - model_started) * 1000,
                2,
            )

    audio = {
        "raw_audio_url": None,
        "normalized_audio_url": None,
        "native_audio_url": None,
        "status": "not-requested",
        "provider": getattr(tts, "name", "unknown"),
        "errors": [],
    }

    if request.include_audio:
        audio = _synthesize_audio(
            original_text=request.text,
            normalized_text=rule.normalized_instruction,
            native_text=(
                rule.spoken_form
                or rule.entity_native
                or rule.entity_kannada
            ),
        )

    total_ms = round((time.perf_counter() - started) * 1000, 2)

    payload = {
        "original_text": request.text,
        "normalized_text": rule.normalized_instruction,
        "rule": rule.model_dump(),
        "model": model_result.model_dump() if model_result else None,
        "model_error": model_error,
        "audio": audio,
        "timings_ms": {
            "rule": rule_ms,
            "model": model_ms,
            "total": total_ms,
        },
        "options": {
            "include_model": request.include_model,
            "include_audio": request.include_audio,
            "adapter_id": request.adapter_id,
        },
    }

    stored = run_store.create(payload)
    payload["run_id"] = stored["run_id"]
    return payload
