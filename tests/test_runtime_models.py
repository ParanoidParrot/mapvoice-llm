import csv

from mapvoice_llm.adapter_registry import AdapterRegistry
from mapvoice_llm.runtime_models import RuntimeModelManager


def test_resolve_active_adapter(tmp_path):
    entity_csv = tmp_path / "entities.csv"

    with entity_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "entity_id",
                "english_name",
                "kannada_name",
                "entity_type",
                "city",
                "language",
                "alternate_spellings",
                "morphemes",
                "suffix",
                "verification_status",
                "pronunciation_verified",
                "source_name",
                "source_url",
                "source_type",
                "reviewer",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "entity_id": "x",
            "english_name": "Example",
            "kannada_name": "ಉದಾಹರಣೆ",
            "entity_type": "locality",
            "city": "Bengaluru",
            "language": "Kannada",
            "alternate_spellings": "",
            "morphemes": "",
            "suffix": "",
            "verification_status": "reviewed",
            "pronunciation_verified": "false",
            "source_name": "",
            "source_url": "",
            "source_type": "",
            "reviewer": "",
            "notes": "",
        })

    registry = AdapterRegistry(tmp_path / "registry.json")
    registry.register({
        "adapter_id": "a1",
        "adapter_path": "/tmp/a1",
        "base_model": "base",
    })
    registry.promote("a1")

    manager = RuntimeModelManager(
        entity_csv=entity_csv,
        base_model_name="base",
        default_adapter_path=None,
        adapter_registry=registry,
    )

    assert manager.resolve_adapter_path(None) == "/tmp/a1"
    assert manager.resolve_adapter_path("base") is None
