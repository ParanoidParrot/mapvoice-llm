from __future__ import annotations


def load_tokenizer(model_name: str, *, trust_remote_code: bool = True, prefer_fast: bool = True):
    """Load a tokenizer with a safe fast->slow fallback for SentencePiece models."""
    from transformers import AutoTokenizer

    errors=[]
    order=[True,False] if prefer_fast else [False]
    for use_fast in order:
        try:
            tokenizer=AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=trust_remote_code,
                use_fast=use_fast,
            )
            return tokenizer, {"use_fast":use_fast,"fallback_used": prefer_fast and not use_fast,"errors":errors}
        except Exception as exc:
            errors.append({"use_fast":use_fast,"error":f"{type(exc).__name__}: {exc}"})
    detail="; ".join(item["error"] for item in errors)
    raise RuntimeError(f"Unable to load tokenizer for {model_name}. {detail}")
