import sys, types
from mapvoice_llm.tokenizer_loader import load_tokenizer

def test_tokenizer_loader_falls_back(monkeypatch):
    class AutoTokenizer:
        @classmethod
        def from_pretrained(cls, model_name, **kwargs):
            if kwargs.get('use_fast'):
                raise ValueError('fast unavailable')
            return object()
    fake=types.SimpleNamespace(AutoTokenizer=AutoTokenizer)
    monkeypatch.setitem(sys.modules,'transformers',fake)
    tokenizer,info=load_tokenizer('x',prefer_fast=True)
    assert tokenizer is not None
    assert info['use_fast'] is False
    assert info['fallback_used'] is True
