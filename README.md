# MapVoice-LLM

MapVoice-LLM is an experimental **regional navigation-language adaptation framework** built on top of the original MapVoice pronunciation-normalization idea. Bengaluru–Kannada is the first active regional pack.

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


## Regional-pack architecture

Bengaluru–Kannada is now represented as a regional pack rather than hard-coded as the only future target. A pack records the city, state, regional language, dataset files, evaluation suites, base model, and optional TTS language code.

```text
configs/regional_packs.json

blr-kn   Bengaluru / Kannada
```

Future packs can reuse the same training, evaluation, adapter registry, API, and UX. For example:

```text
chn-ta     Chennai / Tamil
hyd-te     Hyderabad / Telugu
mum-mr     Mumbai / Marathi
kochi-ml   Kochi / Malayalam
```

Create a new empty pack scaffold with:

```bash
python scripts/create_regional_pack.py \
  --pack-id chn-ta \
  --city Chennai \
  --state Tamil-Nadu \
  --language Tamil \
  --language-code ta \
  --tts-language-code ta-IN
```

This creates empty entity/candidate CSVs and registers the pack. It does **not** invent language labels or mark data as verified.

API:

```text
GET /regional-packs
GET /regional-packs/{pack_id}
```

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

Preferred local-development command:

```bash
python scripts/run_local.py
```

Open:

```text
http://localhost:3000
```

API docs:

```text
http://localhost:3000/docs
```

To choose another configured regional pack:

```bash
python scripts/run_local.py --pack-id hyd-te
```

Equivalent direct Uvicorn command:

```bash
python -m uvicorn mapvoice_llm.api:app \
  --reload \
  --app-dir src \
  --host 127.0.0.1 \
  --port 3000
```

The browser is now organized into four workspaces:

```text
Project console
Pronunciation demo
Data & annotation
Training
Evaluation
```

The project console surfaces the current implementation state, active regional pack,
dataset counts, Python/dependency status, training runs, checkpoints, adapters,
evaluation experiments, readiness gates, TTS status, improvement exports, and
model-hosting export bundles.

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

---

## Preparing an adapter for future model hosting

The project can generate an **offline publication bundle** for a registered adapter. It does not upload anything automatically.

```bash
python scripts/export_hf_bundle.py \
  mapvoice-blr-kn-v1 \
  --pack-id blr-kn \
  --license other
```

Output:

```text
outputs/hf_exports/mapvoice-blr-kn-v1/
├── README.md
└── mapvoice_manifest.json
```

The generated model-card starter contains the base model, regional scope, task, adapter/training-run metadata, evaluation section, limitations, and licensing reminder. Before public hosting, independently verify the base-model license, dataset/source licenses, evaluation quality, and native-speaker review.

This keeps future publication concerns separate from the current training work.


## Language-agnostic entity schema

The first Bengaluru dataset used `english_name` and `kannada_name`. That is now treated as a legacy input format.

The reusable regional-pack schema uses:

```text
latin_name
native_name
language
language_code
```

The existing Bengaluru–Kannada CSV continues to work through a compatibility adapter.

New regional packs created with:

```bash
python scripts/create_regional_pack.py ...
```

use the generic schema automatically.

Inspect the current pack:

```bash
python scripts/pack_status.py --pack-id blr-kn
```

Export the Bengaluru source data into the generic representation without modifying the original:

```bash
python scripts/export_generic_entities.py --pack-id blr-kn
```

## Tokenizer preflight

Training dependency checks now explicitly include:

```text
protobuf
sentencepiece
datasets
transformers
peft
trl
accelerate
```

Run:

```bash
python scripts/doctor.py
python scripts/training_preflight.py
```

Then test the real model tokenizer before a full model load:

```bash
python scripts/tokenizer_preflight.py \
  --model-name sarvamai/sarvam-1
```

To explicitly require the fast tokenizer:

```bash
python scripts/tokenizer_preflight.py \
  --model-name sarvamai/sarvam-1 \
  --use-fast
```

## Selecting a regional pack

The default remains `blr-kn`.

A future configured pack can be selected at runtime:

```bash
export MAPVOICE_PACK_ID=hyd-te
```

Then start the API normally.

Inspect the active pack:

```text
GET /regional-packs/active
```

This allows the same service/runtime to host different regional packs without creating language-specific code forks.


## Project console status API

The UX overview is backed by:

```text
GET /project/status
```

This endpoint deliberately reports local metadata without loading model weights. It includes:

- active regional pack
- Python runtime
- ML dependency availability
- entity/candidate counts
- processed split state
- training-run and checkpoint counts
- adapter registry state
- experiment/improvement-export counts
- optional TTS state
- offline model-hosting export count
- development-stage map



## Pack-aware dataset generation

The original `scripts/build_dataset.py` remains for compatibility with the first Bengaluru dataset.
For regional packs, use:

```bash
python scripts/build_pack_dataset.py --pack-id blr-kn
```

This writes:

```text
data/processed/packs/blr-kn/
├── all.jsonl
├── train.jsonl
├── validation.jsonl
├── test.jsonl
└── manifest.json
```

The split is entity-level, so one place entity is not intentionally spread across train/validation/test.
A future pack uses the same command, for example `--pack-id hyd-te`.

## Training workspace

The browser now has a dedicated **Training** workspace. It provides reusable profiles and generates the full LoRA command instead of requiring you to remember the flags.

Profiles:

```text
local-mac
cuda-qlora
```

API:

```text
GET  /training/profiles
POST /training/plan
POST /training/build-pack-dataset
```

The planner only creates a transparent plan/command; it does not launch a long-running training process from the browser.

## Tokenizer fallback

Model and training tokenizer loading now prefers a fast tokenizer but can fall back to the slow SentencePiece tokenizer when the fast conversion path is incompatible. This is useful for models such as Sarvam-1 while still keeping `protobuf` and `sentencepiece` explicit dependencies.

## Experiment comparison

Saved evaluation runs can now be compared in the Evaluation workspace.

```text
POST /experiments/compare
```

The comparison shows second-minus-first deltas for entity exact match, spoken-form exact match, CER, and runtime. Higher exact-match is better; lower CER is better.


## TTS troubleshooting

The demo now automatically enables **Generate audio** whenever Sarvam is correctly configured.

Install/update the TTS dependencies:

```bash
python -m pip install -r requirements-tts.txt
```

Create `.env` from the example and add:

```text
SARVAM_API_KEY=...
```

`MAPVOICE_TTS_ENABLED` can be left blank. When the API key is present, TTS auto-enables.

Check configuration without making a paid/network synthesis request:

```bash
python scripts/tts_diagnostic.py
```

Make one real diagnostic request:

```bash
python scripts/tts_diagnostic.py --synthesize
```

This writes:

```text
outputs/generated_audio/tts_diagnostic.wav
```

Current integration uses Sarvam Bulbul v3 by default:

```text
SARVAM_TTS_MODEL=bulbul:v3
SARVAM_TTS_SPEAKER=shubh
```

The demo sends raw/normalized navigation English as `en-IN` and native text using the active regional pack language code.

## Parallel Indian-language packs

The repository now contains five regional packs:

```text
blr-kn    Bengaluru / Kannada
chn-ta    Chennai / Tamil
hyd-te    Hyderabad / Telugu
mum-mr    Mumbai / Marathi
kochi-ml  Kochi / Malayalam
```

The four new packs begin as **scaffolds**, not trained or linguistically verified models.

Each new pack has:

- regional metadata
- TTS language configuration
- empty generic entity dataset
- 20 Latin-script locality candidates
- annotation queue
- generic dataset/training compatibility
- LoRA training-plan support
- future model-card/Hugging Face export support

Native-script forms are intentionally blank until reviewed rather than being generated as authoritative labels.

Inspect all packs in the Project Console or:

```text
GET /regional-packs/status
```

Run a specific pack:

```bash
python scripts/run_local.py --pack-id chn-ta
python scripts/run_local.py --pack-id hyd-te
python scripts/run_local.py --pack-id mum-mr
python scripts/run_local.py --pack-id kochi-ml
```

Candidate status:

```bash
python scripts/candidate_status.py --pack-id chn-ta
```

After native labels and sources are reviewed:

```bash
python scripts/promote_candidates.py \
  --pack-id chn-ta \
  --dry-run
```

Generic validation:

```bash
python scripts/validate_pack_entities.py --pack-id chn-ta
```


## Multilingual training-data quality pipeline

The backend now treats training-data quality as an explicit build policy.

Available policies:

```text
labeled
reviewed
verified
pronunciation-verified
```

Build Bengaluru/Kannada using all currently labeled rows:

```bash
python scripts/build_pack_dataset.py \
  --pack-id blr-kn \
  --policy labeled
```

Build a stricter future corpus:

```bash
python scripts/build_pack_dataset.py \
  --pack-id blr-kn \
  --policy verified
```

Outputs are separated by policy:

```text
data/processed/packs/<pack-id>/<policy>/
├── all.jsonl
├── train.jsonl
├── validation.jsonl
├── test.jsonl
├── manifest.json
├── excluded_entities.json
└── label_audit.json
```

The manifest records source/included/excluded entity counts and why rows were excluded.

### Script-aware label audit

Each language has an expected Unicode script profile:

```text
Kannada     kn
Tamil       ta
Telugu      te
Marathi     mr / Devanagari
Malayalam   ml
```

Audit all packs:

```bash
python scripts/audit_language_labels.py --all
```

Or one pack:

```bash
python scripts/audit_language_labels.py --pack-id chn-ta
```

This catches missing native labels and likely wrong-script labels without attempting to invent or correct translations.

### Importing training-data candidates

Additional place candidates can be imported from a CSV:

```bash
python scripts/import_pack_candidates.py \
  --pack-id hyd-te \
  --source-csv /path/to/source.csv
```

Accepted input columns include:

```text
latin_name
entity_type
native_name
source_name
source_url
notes
```

`native_name` is optional. Imported rows remain candidates until reviewed.

The importer deduplicates against both existing entities and candidate rows.

### Batch corpus build

Build all configured packs in parallel-ready form:

```bash
python scripts/build_all_packs.py --policy labeled
```

Hindi is intentionally not configured in the project at this stage.

### Pack-specific evaluation scaffolds

Generate generic evaluation files for a regional pack:

```bash
python scripts/build_pack_evaluation.py --pack-id mum-mr
```

Until reviewed native labels exist, new-language evaluation manifests explicitly report an empty/not-ready state.


## Large-source candidate ingestion

v1.8 adds backend-only ingestion/review/provenance tooling for Tamil, Telugu, Marathi and Malayalam (also usable for Kannada).

The recommended large source is a downloaded OpenStreetMap extract/derived file rather than bulk querying public Nominatim.

Registered sources:

```bash
python scripts/source_registry.py
```

For Chennai, Hyderabad and Kochi use a local file derived from the Geofabrik Southern Zone extract. For Mumbai use a local file derived from the Western Zone extract.

After obtaining/exporting a city-filtered GeoJSON:

```bash
python scripts/migrate_candidate_schema.py --all

python scripts/ingest_source_candidates.py \
  --pack-id chn-ta \
  --source-id osm-geofabrik-southern-zone \
  --format geojson \
  --input /path/to/chennai_places.geojson
```

The GeoJSON reader recognizes common OSM properties such as:

```text
name
name:en
name:ta / name:te / name:mr / name:ml
place
@id / osm_id
```

CSV ingestion is also supported:

```bash
python scripts/ingest_source_candidates.py \
  --pack-id mum-mr \
  --source-id curated-local-file \
  --format csv \
  --input /path/to/mumbai_places.csv
```

Then inspect provenance:

```bash
python scripts/provenance_status.py --pack-id chn-ta
```

Build a review queue:

```bash
python scripts/build_review_queue.py \
  --pack-id chn-ta \
  --limit 500
```

Each ingestion writes an immutable manifest with SHA-256 input hash under:

```text
data/provenance/ingestions/
```

Ingestion does not promote rows to verified training data.


## Base-model bake-off

The base model is now a benchmarked dependency rather than a hard-coded assumption.

Configured candidates:

```text
sarvam-1
qwen2.5-1.5b-instruct
gemma3-1b-it
```

Inspect:

```bash
python scripts/base_models.py
```

Plan a Bengaluru/Kannada benchmark without loading models:

```bash
python scripts/benchmark_base_models.py \
  --pack-id blr-kn \
  --policy labeled \
  --limit 24 \
  --plan-only
```

Tokenizer-only comparison:

```bash
python scripts/benchmark_base_models.py \
  --pack-id blr-kn \
  --policy labeled \
  --limit 24 \
  --tokenizer-only
```

Full task benchmark (downloads/loads each selected model):

```bash
python scripts/benchmark_base_models.py \
  --pack-id blr-kn \
  --policy labeled \
  --limit 24
```

Or benchmark selected models:

```bash
python scripts/benchmark_base_models.py \
  --pack-id blr-kn \
  --models sarvam-1,qwen2.5-1.5b-instruct \
  --limit 24
```

Results are written under:

```text
outputs/base_model_benchmarks/
```

The harness reports model/license metadata, tokenizer efficiency and the same task metrics used elsewhere in MapVoice. It uses a transparent task ordering rather than pretending to produce a universal LLM score.

## First Bengaluru/Kannada adapter lifecycle

The first adapter is named:

```text
mapvoice-blr-kn-v1
```

Prepare its corpus/evaluation/training plan:

```bash
python scripts/kannada_adapter.py --prepare
```

Show current artifact/registry status:

```bash
python scripts/kannada_adapter.py --status
```

Run training only:

```bash
python scripts/kannada_adapter.py \
  --train \
  --profile local-mac \
  --dataset-policy labeled
```

On a CUDA machine:

```bash
python scripts/kannada_adapter.py \
  --train \
  --profile cuda-qlora \
  --dataset-policy labeled
```

After training, evaluate base vs adapter:

```bash
python scripts/kannada_adapter.py \
  --evaluate \
  --dataset-policy labeled \
  --limit 24
```

Complete train → evaluate → offline export:

```bash
python scripts/kannada_adapter.py \
  --all \
  --profile local-mac \
  --dataset-policy labeled
```

Promotion is deliberately opt-in:

```bash
python scripts/kannada_adapter.py \
  --evaluate \
  --promote-if-passes
```

Qualification has two levels:

```text
prototype
publishable
```

A `labeled` corpus can qualify as a prototype if it improves the held-out benchmark, but it cannot qualify as publishable. Publishable status requires a reviewed/verified dataset policy plus stricter metric gates.
