from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .entity_repository import RegionalEntityRepository
from .regional_packs import RegionalPack, RegionalPackRegistry


@dataclass(frozen=True)
class PackContext:
    project_root: Path
    pack: RegionalPack

    @property
    def entity_csv(self) -> Path:
        return self.project_root / self.pack.entity_file

    @property
    def candidate_csv(self) -> Path | None:
        if not self.pack.candidate_file:
            return None
        return self.project_root / self.pack.candidate_file

    @property
    def entity_repository(self) -> RegionalEntityRepository:
        return RegionalEntityRepository(
            self.entity_csv,
            language_code=self.pack.region_language_code,
        )


def load_pack_context(
    project_root: str | Path,
    pack_id: str | None = None,
) -> PackContext:
    project_root = Path(project_root)
    registry = RegionalPackRegistry(
        project_root / "configs" / "regional_packs.json"
    )
    pack = registry.get(pack_id) if pack_id else registry.default()
    return PackContext(project_root=project_root, pack=pack)
