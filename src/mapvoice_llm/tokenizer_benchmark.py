from __future__ import annotations

from statistics import mean
from pathlib import Path

from .dataset import read_jsonl
from .prompts import build_prompt
from .tokenizer_loader import load_tokenizer


def _target_native(row: dict) -> str:
    target = row.get("target") or {}
    return (
        target.get("place_name_native")
        or target.get("place_name_kn")
        or target.get("spoken_form")
        or ""
    )


def tokenizer_diagnostics(
    *,
    model_name: str,
    test_file: str | Path,
    limit: int | None = None,
) -> dict:
    rows = read_jsonl(test_file)
    if limit is not None:
        rows = rows[:limit]

    tokenizer, info = load_tokenizer(
        model_name,
        trust_remote_code=True,
        prefer_fast=True,
    )

    prompt_counts = []
    native_counts = []
    latin_counts = []

    for row in rows:
        prompt = build_prompt(**row["input"])
        prompt_counts.append(
            len(tokenizer(prompt, add_special_tokens=False)["input_ids"])
        )

        native = _target_native(row)
        latin = (row.get("target") or {}).get("place_name") or ""

        native_counts.append(
            len(tokenizer(native, add_special_tokens=False)["input_ids"])
            if native
            else 0
        )
        latin_counts.append(
            len(tokenizer(latin, add_special_tokens=False)["input_ids"])
            if latin
            else 0
        )

    count = len(rows)
    native_total = sum(native_counts)
    latin_total = sum(latin_counts)

    return {
        "examples": count,
        "tokenizer_class": type(tokenizer).__name__,
        "use_fast": info.get("use_fast"),
        "fallback_used": info.get("fallback_used"),
        "mean_prompt_tokens": round(mean(prompt_counts), 2) if prompt_counts else 0,
        "mean_native_name_tokens": round(mean(native_counts), 2) if native_counts else 0,
        "mean_latin_name_tokens": round(mean(latin_counts), 2) if latin_counts else 0,
        "native_to_latin_token_ratio": (
            round(native_total / latin_total, 4)
            if latin_total
            else None
        ),
    }
