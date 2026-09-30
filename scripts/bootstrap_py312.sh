#!/usr/bin/env bash
set -euo pipefail
if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif command -v brew >/dev/null 2>&1 && [[ -x "$(brew --prefix python@3.12 2>/dev/null)/bin/python3.12" ]]; then
  PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
else
  echo "Python 3.12 was not found."
  echo "On macOS: brew install python@3.12"
  exit 1
fi

echo "Using: $PYTHON_BIN"
"$PYTHON_BIN" --version
if [[ -d ".venv" ]]; then
  echo "Existing .venv found. Remove it first: rm -rf .venv"
  exit 1
fi
"$PYTHON_BIN" -m venv .venv
echo "Created .venv with Python 3.12."
echo "Next:"
echo "  source .venv/bin/activate"
echo "  python -m pip install --upgrade pip setuptools wheel"
echo "  python -m pip install -r requirements-training.txt"
echo "  python scripts/doctor.py"
echo "  python scripts/training_preflight.py"
