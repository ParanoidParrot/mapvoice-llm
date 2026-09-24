from __future__ import annotations

from pathlib import Path

from .adapter_registry import AdapterRegistry
from .engine import MapVoiceEngine


class RuntimeModelManager:
    def __init__(
        self,
        *,
        entity_csv: str | Path,
        base_model_name: str | None,
        default_adapter_path: str | None,
        adapter_registry: AdapterRegistry,
    ):
        self.entity_csv = Path(entity_csv)
        self.base_model_name = base_model_name
        self.default_adapter_path = default_adapter_path
        self.registry = adapter_registry

        self.base_engine = MapVoiceEngine(
            entity_csv=self.entity_csv,
            model_name=base_model_name,
            adapter_path=default_adapter_path,
        )
        self._engines: dict[str, MapVoiceEngine] = {}

    def resolve_adapter_path(
        self,
        adapter_id: str | None,
    ) -> str | None:
        if adapter_id == "base":
            return None

        if adapter_id:
            adapter = self.registry.get(adapter_id)
            if adapter is None:
                raise KeyError(adapter_id)
            return adapter.get("adapter_path")

        active = self.registry.active()
        if active:
            return active.get("adapter_path")

        return self.default_adapter_path

    def model_engine(
        self,
        adapter_id: str | None = None,
    ) -> MapVoiceEngine:
        adapter_path = self.resolve_adapter_path(adapter_id)
        cache_key = adapter_path or "__base__"

        if cache_key not in self._engines:
            self._engines[cache_key] = MapVoiceEngine(
                entity_csv=self.entity_csv,
                model_name=self.base_model_name,
                adapter_path=adapter_path,
            )

        return self._engines[cache_key]

    def clear_cache(self) -> None:
        self._engines.clear()
