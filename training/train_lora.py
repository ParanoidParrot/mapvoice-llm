"""
MapVoice Bengaluru-Kannada LoRA/QLoRA training entry point.

Important macOS note:
- Default quantization is "none".
- QLoRA/bitsandbytes 4-bit is intended primarily for a compatible CUDA GPU.
- Apple Silicon MPS is detected, but serious training of a 2B model may still be too
  memory-intensive for a MacBook Air. The same script can be moved to a cloud GPU.

The data split must be entity-level before this script is run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.prompts import format_sft_example


def read_jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="sarvamai/sarvam-1")
    parser.add_argument("--train-file", required=True)
    parser.add_argument("--validation-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=16)
    parser.add_argument(
        "--quantization",
        choices=["none", "4bit"],
        default="none",
        help="Use 4bit only on a compatible CUDA environment.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def hardware():
    import torch

    if torch.cuda.is_available():
        return "cuda", torch.bfloat16, True

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", torch.float16, False

    return "cpu", torch.float32, False


def main() -> None:
    import torch

    args = parse_args()
    device_name, dtype, supports_bf16 = hardware()

    if args.quantization == "4bit" and device_name != "cuda":
        raise SystemExit(
            "4-bit QLoRA was requested, but no CUDA GPU is available. "
            "Use --quantization none locally or move the run to a CUDA GPU."
        )

    train_dataset = Dataset.from_list(
        [format_sft_example(x) for x in read_jsonl(args.train_file)]
    )
    validation_dataset = Dataset.from_list(
        [format_sft_example(x) for x in read_jsonl(args.validation_file)]
    )

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = {
        "trust_remote_code": True,
        "torch_dtype": dtype,
    }

    if device_name != "mps":
        model_kwargs["device_map"] = "auto"

    if args.quantization == "4bit":
        from transformers import BitsAndBytesConfig

        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    print(
        json.dumps(
            {
                "device": device_name,
                "dtype": str(dtype),
                "quantization": args.quantization,
                "train_examples": len(train_dataset),
                "validation_examples": len(validation_dataset),
            },
            indent=2,
        )
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        **model_kwargs,
    )

    if device_name == "mps":
        model = model.to("mps")

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",
    )

    training_args = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.grad_accum,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=5,
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        max_length=args.max_length,
        dataset_text_field="text",
        report_to="none",
        seed=args.seed,
        bf16=supports_bf16,
        fp16=(device_name == "cuda" and not supports_bf16),
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        peft_config=peft_config,
        processing_class=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Saved adapter to {args.output_dir}")


if __name__ == "__main__":
    main()
