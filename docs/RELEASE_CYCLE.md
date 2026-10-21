# MapVoice dataset release cycle

## v0.1 preview
Purpose: public timestamp and project discovery.

## v0.2 reviewed
Gate: at least 20 consensus-reviewed rows from at least one regional pack.

## multilingual-reviewed milestone
Gate: at least 40 reviewed rows spanning two regional packs.

## v0.3 pilot
Gate: at least one regional pack has a frozen pilot manifest.

Each release should include `dataset_snapshot.json`; use `compare_hf_releases.py`
to produce a machine-readable diff before publishing.
