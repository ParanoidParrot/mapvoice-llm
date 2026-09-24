# MapVoice-LLM

Experimental **Bengaluru–Kannada geographic language adaptation** project for MapVoice.

Current repository stage: **v0.2 training/evaluation scaffold**.

The project does **not** initially train a speech synthesizer. It trains/adapts a language
model to understand Bengaluru navigation strings and produce a Kannada-aware pronunciation
representation. A TTS engine remains downstream.

---

## Current pipeline

```text
navigation instruction
        |
        v
normalization
        |
        +------ exact city lexicon / rule baseline
        |
        +------ base or LoRA-adapted language model
                         |
                         v
                 structured JSON
                         |
                         v
              pronunciation target
                         |
                         v
                   downstream TTS
```

## What v0.2 contains

- deterministic rule baseline
- seed Bengaluru/Kannada lexicon
- generated navigation examples
- **entity-level** train/validation/test splitting
- dataset manifest + validator
- stable prompt/target format
- JSON model-output parser
- lazy Hugging Face inference backend
- base-model / PEFT adapter inference path
- baseline benchmark
- model benchmark
- tokenizer inspection utility
- LoRA/QLoRA training entry point
- macOS/CUDA environment doctor
- FastAPI API with rule/model backend selection
- tests

The seed Kannada spellings are intentionally marked `verified=false`; they are scaffolding,
not a claim of authoritative linguistic annotation.

---

# 1. Setup

For API + lightweight development only:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-core.txt
```

For model training/evaluation:

```bash
pip install -r requirements-training.txt
```

Check the active environment:

```bash
python scripts/doctor.py
```

On your Mac, `python`, `pip`, and `uvicorn` should all resolve to the same `.venv`.

---

# 2. Validate and build the dataset

```bash
python scripts/validate_entities.py
python scripts/build_dataset.py
```

or:

```bash
make validate
make build
```

Generated files:

```text
data/processed/navigation_examples.jsonl
data/processed/train.jsonl
data/processed/validation.jsonl
data/processed/test.jsonl
data/processed/manifest.json
```

Splitting is done by **entity**, not by sentence. If `Jayanagar` is in training, no generated
`Jayanagar` sentence is allowed into validation/test.

---

# 3. Run tests

```bash
pytest -q
```

---

# 4. Run the rule baseline

```bash
python scripts/benchmark.py
```

The seed dataset is lookup-friendly, so this baseline is deliberately strong for *seen lexicon*
items. Later hard/unseen-name evaluation is what will make the ML comparison meaningful.

---

# 5. Start the API

```bash
python -m uvicorn mapvoice_llm.api:app --reload --app-dir src
```

Health:

```bash
curl http://127.0.0.1:8000/health
```

Rule backend:

```bash
curl -X POST http://127.0.0.1:8000/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Turn left onto Kanakapura Rd after 500m",
    "backend":"rule"
  }'
```

The model is **lazy-loaded**, so running the API does not immediately load Sarvam-1.

Model backend:

```bash
curl -X POST http://127.0.0.1:8000/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Continue towards Jayanagar",
    "backend":"model"
  }'
```

The first `backend=model` request may load a large model and can be slow/memory-intensive.

---

# 6. Inspect Kannada tokenization

Before training, inspect how the candidate tokenizer handles Bengaluru English/Kannada forms:

```bash
python scripts/inspect_tokenization.py \
  --model-name sarvamai/sarvam-1
```

Later run the same command against alternative models and compare token counts.

---

# 7. First LoRA training experiment

## Mac / Apple Silicon

Start with no quantization:

```bash
python training/train_lora.py \
  --model-name sarvamai/sarvam-1 \
  --train-file data/processed/train.jsonl \
  --validation-file data/processed/validation.jsonl \
  --output-dir artifacts/mapvoice-blr-kn-v0.1 \
  --quantization none
```

This does **not** mean a MacBook Air will necessarily have enough memory for useful 2B-model
training. The code detects MPS, but hardware capacity remains a real constraint.

## CUDA GPU / cloud GPU

For a compatible CUDA setup:

```bash
python training/train_lora.py \
  --model-name sarvamai/sarvam-1 \
  --train-file data/processed/train.jsonl \
  --validation-file data/processed/validation.jsonl \
  --output-dir artifacts/mapvoice-blr-kn-v0.1 \
  --quantization 4bit
```

QLoRA uses LoRA adapters on all linear modules.

---

# 8. Evaluate a base model

Use a small limit first:

```bash
python scripts/evaluate_model.py \
  --model-name sarvamai/sarvam-1 \
  --limit 5
```

The report is written to:

```text
outputs/model_eval.json
```

---

# 9. Evaluate a trained adapter

```bash
python scripts/evaluate_model.py \
  --model-name sarvamai/sarvam-1 \
  --adapter-path artifacts/mapvoice-blr-kn-v0.1
```

For API inference with an adapter:

```bash
export MAPVOICE_MODEL_NAME=sarvamai/sarvam-1
export MAPVOICE_ADAPTER_PATH=artifacts/mapvoice-blr-kn-v0.1

python -m uvicorn mapvoice_llm.api:app --reload --app-dir src
```

---

# Repository layout

```text
mapvoice-llm/
├── configs/
├── data/
│   ├── raw/
│   └── processed/
├── evaluation/
│   └── metrics.py
├── scripts/
│   ├── benchmark.py
│   ├── build_dataset.py
│   ├── doctor.py
│   ├── evaluate_model.py
│   ├── inspect_tokenization.py
│   ├── run_api.py
│   └── validate_entities.py
├── src/mapvoice_llm/
│   ├── api.py
│   ├── baseline.py
│   ├── config.py
│   ├── dataset.py
│   ├── engine.py
│   ├── lexicon.py
│   ├── model_backend.py
│   ├── normalization.py
│   ├── prompts.py
│   ├── response_parser.py
│   └── schemas.py
├── tests/
├── training/
│   └── train_lora.py
├── Makefile
├── requirements-core.txt
├── requirements-training.txt
└── pyproject.toml
```

---

# Next meaningful development milestone

Do **not** scale training examples by repeatedly templating the same 20 names.

Next we should build a proper `bengaluru_entities_v0.2.csv` with roughly 100–150 manually
reviewed entities and explicitly separate:

1. **lexicon-known test** — measures the hybrid system
2. **entity-held-out test** — measures memorization/generalization
3. **morphological hard set** — measures behavior on difficult Kannada-derived place names

After that, the first model run will tell us something scientifically useful.

---

## Model-license note

The default model name is only an experimental configuration. Verify the selected base model's
license before publishing adapters or using them commercially.


---

# v0.4 dataset workflow

v0.4 introduces a strict distinction between entity verification and pronunciation verification.

```bash
python scripts/validate_entities.py
python scripts/dataset_status.py
python scripts/create_annotation_sheet.py
python scripts/annotate_morphology.py
python scripts/build_dataset.py
python scripts/build_holdouts.py
python scripts/lint_dataset.py
pytest -q
```

For a strict training build later:

```bash
python scripts/build_dataset.py \
  --verified-only \
  --pronunciation-verified-only
```

The build intentionally fails if no entities satisfy those gates.

New important files:

```text
data/raw/bengaluru_entities_v0.4.csv
outputs/annotation_queue.csv
data/raw/bengaluru_entities_v0.4_morphology.csv
data/evaluation/generated_hard_holdout.jsonl
configs/dataset_registry.json
configs/experiment_v0.4.yaml
```

Morphology annotations are heuristics and must be manually reviewed before being treated as ground truth.


---

# v0.5 — MapVoice-style web UX

v0.5 adds the first browser UX for the LLM project while preserving the existing MapVoice demo
shape:

```text
English navigation input
        ↓
normalized text
        ↓
rule baseline / LLM comparison
        ↓
Kannada native-language target
        ↓
future raw / normalized / Kannada audio comparison
```

The right-hand panel retains the MapVoice demo convention of **sample selection + language
selection**, with additional experiment/model and dataset status.

Start it with:

```bash
source .venv/bin/activate
python -m uvicorn mapvoice_llm.api:app --reload --app-dir src
```

Then open:

```text
http://127.0.0.1:8000/
```

or:

```text
http://127.0.0.1:8000/demo
```

New endpoints:

```text
GET  /
GET  /demo
GET  /demo/samples
GET  /dataset/status
POST /demo/compare
```

Example compare request:

```bash
curl -X POST http://127.0.0.1:8000/demo/compare \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Turn left onto Kanakapura Rd after 500m",
    "include_model": false
  }'
```

The web demo defaults to the deterministic rule engine. Turn on **Compare model** in the
right-side panel only when you want to load/run the configured Hugging Face model.

Audio buttons are intentionally disabled in v0.5. They mark the integration surface for the
existing MapVoice TTS pipeline; the UI does not pretend audio exists before that backend is
connected.


---

# v0.6 — Optional TTS + run history + candidate corpus

v0.6 connects the MapVoice-style UX to an actual audio-provider contract while keeping TTS
optional.

## TTS

Install the optional provider dependencies:

```bash
pip install -r requirements-tts.txt
```

Configure:

```bash
cp .env.example .env

export MAPVOICE_TTS_ENABLED=true
export SARVAM_API_KEY="..."
```

Or load `.env` in your shell/tooling before starting the API.

Then:

```bash
python -m uvicorn mapvoice_llm.api:app --reload --app-dir src
```

Check:

```bash
curl http://127.0.0.1:8000/tts/status
```

The demo can now request:

```text
raw navigation audio
normalized navigation audio
Kannada/native-form audio
```

Generated clips are stored under:

```text
outputs/generated_audio/
```

and served through:

```text
/audio/<filename>
```

The demo remains functional when TTS is disabled or unavailable.

## Demo run history

Each `/demo/compare` call is archived locally as JSON:

```text
outputs/demo_runs/
```

Endpoints:

```text
GET /demo/runs
GET /demo/runs/{run_id}
```

This gives us a lightweight trace of experiments before introducing a database.

## Candidate corpus

v0.6 adds:

```text
data/seeds/bengaluru_candidates_v0.6.csv
```

with 60 English-name Bengaluru candidate entities. These are intentionally **not** treated as
verified training data. Kannada forms and provenance are blank until reviewed.

Inspect:

```bash
python scripts/candidate_status.py
```

After manually setting candidate rows to `annotation_status=reviewed` and adding both
`kannada_name` and `source_name`, preview promotion:

```bash
python scripts/promote_candidates.py --dry-run
```

Promote reviewed candidates:

```bash
python scripts/promote_candidates.py
```

Promoted rows enter the main entity file as `verification_status=reviewed`, not fully verified.

## UI

The v0.6 demo adds:

- Generate audio toggle
- real browser audio players
- TTS provider status
- per-run timing
- persistent local run IDs
- recent-run history in the right panel

The UX still defaults to lightweight rule comparison; it only loads the LLM or TTS provider
when the respective toggle is enabled.


---

# v0.7 — Experiment dashboard + browser annotation

v0.7 adds two larger development surfaces.

## 1. Evaluation experiments

You can benchmark the current processed test split directly from the browser or API.

Endpoints:

```text
POST /experiments/evaluate
GET  /experiments
GET  /experiments/{experiment_id}
```

Rule baseline example:

```bash
curl -X POST http://127.0.0.1:8000/experiments/evaluate \
  -H "Content-Type: application/json" \
  -d '{"backend":"rule","limit":10}'
```

Configured model / adapter:

```bash
curl -X POST http://127.0.0.1:8000/experiments/evaluate \
  -H "Content-Type: application/json" \
  -d '{"backend":"model","limit":5}'
```

Model evaluation may load a large Hugging Face model and should therefore be started with a small
limit on local hardware.

Experiment reports are stored in:

```text
outputs/experiments/
```

CLI rule benchmark:

```bash
python scripts/evaluate_rule.py --limit 10
python scripts/experiment_status.py
```

## 2. Browser candidate annotation

The demo page now includes a candidate review form.

Endpoints:

```text
GET   /annotations/candidates
GET   /annotations/candidates/{candidate_id}
PATCH /annotations/candidates/{candidate_id}
```

Example:

```bash
curl -X PATCH \
  http://127.0.0.1:8000/annotations/candidates/cand_0001 \
  -H "Content-Type: application/json" \
  -d '{
    "kannada_name":"...",
    "source_name":"review source",
    "source_url":"https://...",
    "annotation_status":"reviewed"
  }'
```

This edits:

```text
data/seeds/bengaluru_candidates_v0.6.csv
```

The annotation UI is intentionally a local-development workflow. For multi-user annotation, move
this repository layer to a real database before exposing it remotely.

## UI additions

v0.7 now has:

- benchmark backend selector
- benchmark sample limit
- entity exact-match metric
- spoken-form exact-match metric
- mean character-error-rate metric
- benchmark runtime
- browser candidate selector
- Kannada-name annotation
- source metadata annotation
- review/reject actions


---

# v0.8 — Evaluation suites, error explorer, and training readiness

v0.8 separates benchmarks by evaluation intent.

Available suites:

```text
entity-held-out
lexicon-known
morphological-hard
generated-hard-holdout
```

List suites:

```bash
curl http://127.0.0.1:8000/evaluation/suites
```

Run a specific benchmark:

```bash
curl -X POST http://127.0.0.1:8000/experiments/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "backend":"rule",
    "suite_id":"morphological-hard",
    "limit":10
  }'
```

CLI:

```bash
python scripts/evaluate_suite.py \
  --suite morphological-hard \
  --limit 10
```

The web UX now shows the highest-character-error-rate examples after each benchmark so failures
are visible rather than hidden behind aggregate metrics.

## Training readiness

Endpoint:

```text
GET /training/readiness
```

CLI:

```bash
python scripts/training_readiness.py
```

Current strict gates are intentionally conservative:

```text
50+ verified entities
25+ pronunciation-verified entities
3+ verified entity types
```

The UI displays these gates explicitly. The project should not treat model metrics as meaningful
training results until the dataset clears these basic quality gates.


---

# v0.9 — Failure taxonomy and improvement-dataset export

v0.9 makes benchmark failures actionable.

Each evaluation row can now be classified into explicit failure categories:

```text
invalid_json
missing_entity
wrong_entity
missing_kannada
wrong_kannada
missing_spoken_form
wrong_spoken_form
high_cer
suffix_failure
unknown_entity
```

The benchmark UI shows category counts and per-example failure tags.

## Export failed examples

API:

```text
POST /experiments/export-improvement
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/experiments/export-improvement \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":"exp_..."}'
```

Outputs are written under:

```text
outputs/improvement_datasets/
```

CLI:

```bash
python scripts/failure_report.py exp_...
python scripts/export_improvement_dataset.py exp_...
```

The exported JSONL keeps:

```text
input text
target
prediction
suite
metrics
failure categories
```

This becomes the bridge between evaluation and the next fine-tuning/data-improvement cycle.


---

# v1.0 — Training lifecycle and adapter promotion

v1.0 closes the loop between training and the demo.

## Training run metadata

Every `training/train_lora.py` run now creates a record under:

```text
outputs/training_runs/
```

Run with automatic adapter registration:

```bash
python training/train_lora.py \
  --model-name sarvamai/sarvam-1 \
  --train-file data/processed/train.jsonl \
  --validation-file data/processed/validation.jsonl \
  --output-dir artifacts/mapvoice-blr-kn-v1 \
  --quantization none \
  --adapter-id mapvoice-blr-kn-v1 \
  --register-adapter
```

Inspect runs:

```bash
python scripts/training_runs.py
```

## Adapter registry

Registry:

```text
configs/adapter_registry.json
```

Register an existing adapter:

```bash
python scripts/register_adapter.py \
  mapvoice-blr-kn-v1 \
  artifacts/mapvoice-blr-kn-v1 \
  --base-model sarvamai/sarvam-1
```

Promote it:

```bash
python scripts/promote_adapter.py mapvoice-blr-kn-v1
```

The active adapter is then used by the demo without changing
`MAPVOICE_ADAPTER_PATH`.

API:

```text
GET  /adapters
POST /adapters/register
POST /adapters/promote
POST /adapters/clear-active
```

## Checkpoint discovery

```bash
python scripts/checkpoints.py
```

API:

```text
GET /checkpoints
```

## Training runs API

```text
GET /training/runs
GET /training/runs/{run_id}
```

## Runtime model selection

The MapVoice UI now has a model/adapter selector. You can compare the base model
or any registered adapter without restarting the API.

Direct comparison API:

```text
POST /models/compare
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/models/compare \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Continue towards Jayanagar.",
    "adapter_ids":["base","mapvoice-blr-kn-v1"]
  }'
```

Lifecycle:

```text
dataset
  ↓
training run
  ↓
checkpoint / adapter
  ↓
adapter registry
  ↓
evaluation
  ↓
promotion
  ↓
MapVoice demo
```
