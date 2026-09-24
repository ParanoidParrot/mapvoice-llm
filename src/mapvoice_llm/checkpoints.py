from __future__ import annotations

from pathlib import Path


def discover_checkpoints(artifact_root: str | Path) -> list[dict]:
    root = Path(artifact_root)

    if not root.exists():
        return []

    rows = []

    for path in sorted(root.rglob("checkpoint-*")):
        if not path.is_dir():
            continue

        rows.append({
            "name": path.name,
            "path": str(path),
            "relative_path": str(path.relative_to(root)),
            "has_adapter_config": (path / "adapter_config.json").exists(),
            "has_adapter_weights": any(
                (path / name).exists()
                for name in (
                    "adapter_model.safetensors",
                    "adapter_model.bin",
                )
            ),
        })

    return rows
