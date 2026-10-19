from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--release-dir", required=True)
    parser.add_argument("--private", action="store_true")
    parser.add_argument(
        "--commit-message",
        default="Publish MapVoice dataset preview",
    )
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError as exc:
        raise SystemExit(
            "Install requirements-hf.txt first."
        ) from exc

    release_dir = Path(args.release_dir)
    if not release_dir.is_absolute():
        release_dir = PROJECT_ROOT / release_dir

    required = [
        release_dir / "README.md",
        release_dir / "LICENSE_DATA.md",
        release_dir / "release_manifest.json",
        release_dir / "data" / "preview.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(
            "Release is incomplete: " + ", ".join(missing)
        )

    create_repo(
        repo_id=args.repo_id,
        repo_type="dataset",
        private=args.private,
        exist_ok=True,
    )

    HfApi().upload_folder(
        folder_path=str(release_dir),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=args.commit_message,
    )

    print(
        "Published: "
        f"https://huggingface.co/datasets/{args.repo_id}"
    )


if __name__ == "__main__":
    main()
