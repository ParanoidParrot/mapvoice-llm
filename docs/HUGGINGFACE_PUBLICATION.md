# Hugging Face publication strategy

## Suggested dataset repository

`mapvoice-india-navigation-toponyms`

## Release sequence

- **v0.1-preview** — candidate + labeled/unverified data with maturity/provenance flags.
- **v0.2-reviewed** — first consensus-reviewed rows.
- **v0.3-pilot** — frozen regional pilot splits.
- **v1.0** — only after the reviewed multilingual corpus is substantial enough for stable model experiments.

## Positioning

Avoid unsupported priority claims such as:
- "first Indian place-name dataset"
- "first Indian pronunciation dataset"
- "fully pronunciation verified"

Koel already provides a multilingual Indian locality-pronunciation benchmark.

Defensible wording:

> An early city-specific, provenance-aware Indian navigation-toponym dataset and regional-adapter research project covering Bengaluru/Kannada, Chennai/Tamil, Hyderabad/Telugu, Mumbai/Marathi and Kochi/Malayalam.

Or:

> A public dataset and model-development pipeline for geographically specialized Indian navigation language adaptation, with explicit provenance, independent review, held-out evaluation and regional LoRA adapters.

## Publishing v0.1

Build:

```bash
python scripts/build_hf_dataset_release.py --version 0.1.0
```

Check what you can truthfully claim:

```bash
python scripts/check_hf_release.py \
  --release-dir outputs/hf_datasets/mapvoice-india-toponyms-preview-v0.1.0
```

Authenticate:

```bash
python -m pip install -r requirements-hf.txt
hf auth login
```

Publish:

```bash
python scripts/publish_hf_dataset.py \
  --repo-id YOUR_USERNAME/mapvoice-india-navigation-toponyms \
  --release-dir outputs/hf_datasets/mapvoice-india-toponyms-preview-v0.1.0
```

## Secondary reference data

Koel's locality benchmark may be imported as a **reference source**:

```bash
python scripts/import_koel_reference.py --pack-id chn-ta
```

Reference data is never silently promoted to verified MapVoice labels.
