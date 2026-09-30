# MapVoice-LLM

MapVoice-LLM is an experimental **Bengaluru–Kannada navigation-language adaptation system** built on top of the original MapVoice pronunciation-normalization idea.

The goal is narrow: take an existing pretrained model and specialize it for Bengaluru navigation text, local place names, Kannada-aware spoken forms, and pronunciation-oriented output that can be passed to TTS.

```text
Navigation instruction
        |
        v
Normalization
        |
        +-------------------+
        |                   |
        v                   v
Geographic lexicon      Base / LoRA model
        |                   |
        +---------+---------+
                  |
                  v
       Structured pronunciation output
                  |
                  v
          Optional MapVoice TTS
```

The system remains hybrid on purpose: known entities can be resolved deterministically, while the model is intended to help with variants, unseen names, mixed-language input, and difficult local morphology.

## What is implemented

- FastAPI backend and MapVoice-style browser UX
- navigation normalization and Bengaluru entity lexicon
- Kannada/native-script spoken target representation
- Hugging Face base-model inference
- LoRA/QLoRA training scaffold
- training preflight and Python-runtime checks
- training-run metadata and checkpoint discovery
- adapter registry, selection, comparison, and promotion
- entity-level train / validation / test splitting
- lexicon-known, entity-held-out, and hard evaluation suites
- exact-match and character-error-rate metrics
- failure taxonomy and error explorer
- failed-example export for future improvement training
- browser candidate annotation and provenance workflow
- training-readiness gates
- optional Sarvam TTS integration
- raw / normalized / Kannada audio comparison
- local experiment and run history

---

## 1. Environment

### Use Python 3.12

The training environment is standardized on **Python 3.12**.

Do not use the current project venv with Python 3.14. That combination can fail inside Hugging Face `datasets` / `dill` fingerprinting before the model is even loaded.

On macOS:

```bash
brew install python@3.12
rm -rf .venv
bash scripts/bootstrap_py312.sh
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-training.txt
```

Check the environment:

```bash
python scripts/doctor.py
```

The executable should resolve to the repo venv and the version should be Python 3.12.x.

---

## 2. Dataset build and validation

```bash
python scripts/validate_entities.py
python scripts/dataset_status.py
python scripts/build_dataset.py
python scripts/lint_dataset.py
pytest -q
```

The split is done **by entity**, not by generated sentence, so the same place name does not leak between train, validation, and test.

Raw/working data is under:

```text
data/raw/
data/seeds/
data/processed/
data/evaluation/
```

The candidate annotation workflow keeps entity verification and pronunciation verification separate.

---

## 3. Training preflight

Before any training job, run:

```bash
python scripts/training_preflight.py
```

It checks:

- Python runtime and interpreter path
- installed ML package versions
- train and validation files
- SFT example formatting
- Hugging Face `Dataset.from_list()` construction

That last check intentionally reproduces the first step that previously failed on Python 3.14, so the project now stops with a concise environment error instead of a long serializer traceback.

`training/train_lora.py` also runs the same preflight automatically before importing/loading the heavy model stack.

---

## 4. Run the API and UX

```bash
python -m uvicorn mapvoice_llm.api:app --reload --app-dir src
```

Open:

```text
http://127.0.0.1:8000/
```

API docs:

```text
http://127.0.0.1:8000/docs
```

The UX supports navigation input, original/normalized text, rule-vs-model output, Kannada target display, evaluation, candidate annotation, adapter selection, run history, and optional audio.

---

## 5. Rule/model comparison

Rule-only:

```bash
curl -X POST http://127.0.0.1:8000/demo/compare \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Turn left onto Kanakapura Rd after 500m",
    "include_model":false,
    "include_audio":false
  }'
```

Base model:

```bash
curl -X POST http://127.0.0.1:8000/demo/compare \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Continue towards Jayanagar.",
    "include_model":true,
    "adapter_id":"base"
  }'
```

Models are lazy-loaded only when requested.

---

## 6. Train a LoRA adapter

First:

```bash
python scripts/training_preflight.py
```

Then:

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

### Apple Silicon

Use `--quantization none`. The script detects MPS when available. A 2B-class model may still exceed practical MacBook Air memory, in which case use the same repo on a CUDA/cloud GPU.

### CUDA / QLoRA

On compatible NVIDIA hardware:

```bash
python training/train_lora.py \
  --model-name sarvamai/sarvam-1 \
  --train-file data/processed/train.jsonl \
  --validation-file data/processed/validation.jsonl \
  --output-dir artifacts/mapvoice-blr-kn-v1 \
  --quantization 4bit \
  --adapter-id mapvoice-blr-kn-v1 \
  --register-adapter
```

---

## 7. Training runs, checkpoints, and adapters

Training metadata:

```bash
python scripts/training_runs.py
```

Checkpoint discovery:

```bash
python scripts/checkpoints.py
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

The browser model selector can then use the registered adapter without editing environment variables.

Relevant API endpoints:

```text
GET  /training/runs
GET  /checkpoints
GET  /adapters
POST /adapters/register
POST /adapters/promote
POST /adapters/clear-active
POST /models/compare
```

---

## 8. Evaluation

Available suites:

```text
entity-held-out
lexicon-known
morphological-hard
generated-hard-holdout
```

Run one from CLI:

```bash
python scripts/evaluate_suite.py --suite morphological-hard --limit 10
```

Or use:

```text
POST /experiments/evaluate
```

Metrics currently include JSON validity, entity exact match, spoken-form exact match, character error rate, and elapsed time.

The UX also shows high-error examples and failure categories.

---

## 9. Failure analysis and improvement data

Current failure categories include:

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

Inspect a saved experiment:

```bash
python scripts/failure_report.py exp_...
```

Export failed examples:

```bash
python scripts/export_improvement_dataset.py exp_...
```

Outputs are written under:

```text
outputs/improvement_datasets/
```

Those records preserve input, target, prediction, metrics, suite, and failure labels for future data-improvement/fine-tuning cycles.

---

## 10. Bengaluru annotation workflow

Candidate source:

```text
data/seeds/bengaluru_candidates_v0.6.csv
```

The browser annotation screen lets you add a Kannada form, provenance/source, notes, and review status.

CLI helpers:

```bash
python scripts/candidate_status.py
python scripts/promote_candidates.py --dry-run
python scripts/promote_candidates.py
```

Promotion does not automatically mark pronunciation as verified.

---

## 11. Training readiness

```bash
python scripts/training_readiness.py
```

or:

```text
GET /training/readiness
```

Current quality gates include:

```text
50+ verified entities
25+ pronunciation-verified entities
3+ verified entity types
```

These are internal readiness thresholds, not a claim that the resulting dataset is production-grade.

---

## 12. Optional TTS

Install separately:

```bash
python -m pip install -r requirements-tts.txt
```

Configure:

```bash
export MAPVOICE_TTS_ENABLED=true
export SARVAM_API_KEY="..."
```

Status:

```bash
curl http://127.0.0.1:8000/tts/status
```

When available, the UX can compare raw navigation audio, normalized audio, and Kannada/native-form audio. TTS remains optional and does not block the normalization/training workflow.

---

## Repository layout

```text
mapvoice-llm/
├── configs/
├── data/
│   ├── raw/
│   ├── seeds/
│   ├── processed/
│   └── evaluation/
├── evaluation/
├── outputs/
├── scripts/
├── src/mapvoice_llm/
│   └── tts/
├── training/
│   └── train_lora.py
├── ui/
├── tests/
├── requirements-core.txt
├── requirements-training.txt
├── requirements-tts.txt
└── README.md
```

## Recommended next run

```bash
source .venv/bin/activate
python scripts/doctor.py
python scripts/validate_entities.py
python scripts/build_dataset.py
python scripts/lint_dataset.py
python scripts/training_preflight.py
pytest -q
```

If the preflight succeeds, run the LoRA command above.

The main project limitation at this point is the **quality and scale of the verified Bengaluru–Kannada corpus**, not the surrounding application framework.
