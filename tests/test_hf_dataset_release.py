import csv
from pathlib import Path

from mapvoice_llm.hf_dataset_release import build_hf_release
from mapvoice_llm.publication_readiness import assess_release


def test_repo_preview_builds_and_claims_are_guarded():
    root = Path(__file__).resolve().parents[1]

    result = build_hf_release(
        project_root=root,
        release_name="test-mapvoice-preview",
        version="0.0.test",
    )

    release = root / result["output_dir"]

    assert (release / "README.md").exists()
    assert (release / "release_manifest.json").exists()
    assert (release / "data/preview.csv").exists()

    with (release / "data/preview.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert {"kn", "ta", "te", "mr", "ml"}.issubset({
        row["language_code"] for row in rows
    })

    readiness = assess_release(release)
    assert readiness["allowed_public_claims"]["early_preview_dataset"]
    assert not readiness["allowed_public_claims"]["pronunciation_verified_dataset"]
    assert not readiness["allowed_public_claims"]["training_ready_multilingual_dataset"]
