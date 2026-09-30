from __future__ import annotations

import importlib
import platform
import sys
from dataclasses import dataclass

RECOMMENDED_PYTHON = (3, 12)

@dataclass(frozen=True)
class RuntimeCheck:
    ok: bool
    level: str
    message: str

def python_runtime_check() -> RuntimeCheck:
    version = sys.version_info[:3]
    if version >= (3, 14):
        return RuntimeCheck(
            ok=False,
            level='error',
            message=(
                f'Python {version[0]}.{version[1]}.{version[2]} detected. '
                'MapVoice-LLM training is standardized on Python 3.12. '
                'Python 3.14 can fail inside Hugging Face datasets/dill '
                'fingerprinting before model loading. Recreate .venv with Python 3.12.'
            ),
        )
    if version[:2] != RECOMMENDED_PYTHON:
        return RuntimeCheck(
            ok=True,
            level='warning',
            message=(
                f'Python {version[0]}.{version[1]}.{version[2]} detected. '
                'Python 3.12 is the recommended and tested project runtime.'
            ),
        )
    return RuntimeCheck(
        ok=True,
        level='ok',
        message=f'Python {version[0]}.{version[1]}.{version[2]} is supported.',
    )

def package_version(name: str) -> str | None:
    try:
        module = importlib.import_module(name)
    except Exception:
        return None
    return getattr(module, '__version__', 'unknown')

def environment_snapshot() -> dict:
    return {
        'python': sys.version.split()[0],
        'python_executable': sys.executable,
        'platform': platform.platform(),
        'packages': {
            name: package_version(name)
            for name in ('torch','datasets','dill','transformers','peft','trl','accelerate')
        },
    }
