from __future__ import annotations

import importlib
import platform
import sys


PACKAGES = [
    "fastapi",
    "uvicorn",
    "torch",
    "transformers",
    "datasets",
    "peft",
    "trl",
]


def package_version(name: str) -> str:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        return f"ERROR: {exc}"

    return getattr(module, "__version__", "unknown")


def main() -> None:
    print("MapVoice-LLM environment doctor")
    print("=" * 36)
    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {sys.version.split()[0]}")
    print(f"Platform          : {platform.platform()}")
    print()

    for name in PACKAGES:
        print(f"{name:14}: {package_version(name)}")

    try:
        import torch

        print()
        print(f"CUDA available    : {torch.cuda.is_available()}")
        print(
            "MPS available     : "
            f"{hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()}"
        )

        if torch.cuda.is_available():
            print(f"CUDA device       : {torch.cuda.get_device_name(0)}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
