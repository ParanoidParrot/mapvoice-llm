from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .prompts import build_prompt
from .response_parser import ParsedModelOutput, parse_model_output


@dataclass
class GenerationConfig:
    max_new_tokens: int = 160
    temperature: float = 0.0
    do_sample: bool = False


class TransformersBackend:
    """
    Lazy Hugging Face backend.

    Heavy imports and model loading happen only when this backend is instantiated, so the
    rule-based FastAPI server remains lightweight.
    """

    def __init__(
        self,
        model_name: str,
        adapter_path: str | None = None,
        generation: GenerationConfig | None = None,
    ):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.generation = generation or GenerationConfig()

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            use_fast=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        device_name, dtype = self._choose_device_and_dtype()

        kwargs = {
            "trust_remote_code": True,
            "torch_dtype": dtype,
        }

        # device_map="auto" is useful on CUDA/CPU environments; explicit MPS move is safer
        # for many local macOS setups.
        if device_name != "mps":
            kwargs["device_map"] = "auto"

        self.model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)

        if adapter_path:
            from peft import PeftModel

            self.model = PeftModel.from_pretrained(self.model, adapter_path)

        if device_name == "mps":
            self.model = self.model.to("mps")

        self.device = next(self.model.parameters()).device
        self.model.eval()

    def _choose_device_and_dtype(self):
        torch = self.torch
        if torch.cuda.is_available():
            return "cuda", torch.bfloat16

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # float16 is generally a safer memory choice for inference on Apple Silicon.
            return "mps", torch.float16

        return "cpu", torch.float32

    def generate(
        self,
        text: str,
        city: str = "Bengaluru",
        region_language: str = "Kannada",
        navigation_language: str = "English",
    ) -> ParsedModelOutput:
        prompt = build_prompt(
            text=text,
            city=city,
            region_language=region_language,
            navigation_language=navigation_language,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with self.torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.generation.max_new_tokens,
                do_sample=self.generation.do_sample,
                temperature=(
                    self.generation.temperature
                    if self.generation.do_sample
                    else None
                ),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
        generated = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return parse_model_output(generated)
