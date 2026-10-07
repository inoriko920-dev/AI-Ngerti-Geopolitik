"""W7-002 selected-scope contract."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.application.ai_context import ContextBuildError
from ai_ngerti_geopolitik.application.ai_l2_contracts import MAX_W7_SELECTED_TARGETS


@dataclass(frozen=True, slots=True)
class W7SelectedScope:
    """Explicit application-selected clip IDs admitted to W7 planning."""

    clip_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.clip_ids:
            raise ContextBuildError("W7 selected scope requires at least one clip")
        if len(self.clip_ids) > MAX_W7_SELECTED_TARGETS:
            raise ContextBuildError(
                f"W7 selected scope supports at most {MAX_W7_SELECTED_TARGETS} clips"
            )
        for clip_id in self.clip_ids:
            if not isinstance(clip_id, str) or not clip_id.strip():
                raise ContextBuildError("W7 selected scope requires stable non-empty clip ids")
            if clip_id != clip_id.strip():
                raise ContextBuildError("W7 selected clip ids cannot contain outer whitespace")
        if len(set(self.clip_ids)) != len(self.clip_ids):
            raise ContextBuildError("W7 selected clip ids must be unique")

    @property
    def target_count(self) -> int:
        return len(self.clip_ids)
