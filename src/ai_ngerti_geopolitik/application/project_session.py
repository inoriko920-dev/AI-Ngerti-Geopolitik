"""STEP 11 W1 project lifecycle, dirty-state and autosave owner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.application.commands import CommandBatch, CommandBus
from ai_ngerti_geopolitik.application.ports import ProjectRepositoryPort
from ai_ngerti_geopolitik.domain import ProjectState


class ProjectSessionError(RuntimeError):
    pass


class UnsavedChangesError(ProjectSessionError):
    pass


@dataclass(frozen=True, slots=True)
class ProjectLifecycleSnapshot:
    is_open: bool
    dirty: bool
    current_path: Path | None
    project_id: str | None
    revision: int | None


class ProjectSession:
    def __init__(
        self,
        repository: ProjectRepositoryPort,
        *,
        autosave_catalog: AutosaveCatalogService | None = None,
    ) -> None:
        self.repository = repository
        self.autosave_catalog = autosave_catalog or AutosaveCatalogService(repository)
        self._bus: CommandBus | None = None
        self._session_id: str | None = None
        self._current_path: Path | None = None
        self._saved_hash: str | None = None

    @property
    def is_open(self) -> bool:
        return self._bus is not None

    @property
    def session_id(self) -> str | None:
        """Unique lifecycle identity across close/open, even at equal revisions."""
        return self._session_id

    @property
    def bus(self) -> CommandBus:
        if self._bus is None:
            raise ProjectSessionError("no project is open")
        return self._bus

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    @property
    def current_path(self) -> Path | None:
        return self._current_path

    @property
    def dirty(self) -> bool:
        if self._bus is None:
            return False
        if self._saved_hash is None:
            return True
        return self.state.semantic_hash() != self._saved_hash

    @property
    def snapshot(self) -> ProjectLifecycleSnapshot:
        if self._bus is None:
            return ProjectLifecycleSnapshot(False, False, None, None, None)
        return ProjectLifecycleSnapshot(
            True,
            self.dirty,
            self._current_path,
            self.state.project_id,
            self.state.revision,
        )

    def _guard_replacement(self, discard_unsaved: bool) -> None:
        if self.dirty and not discard_unsaved:
            raise UnsavedChangesError("project has unsaved changes")

    def new_project(
        self,
        project_id: str,
        name: str,
        fps: int = 30,
        *,
        width: int = 1920,
        height: int = 1080,
        aspect_ratio: str = "16:9",
        discard_unsaved: bool = False,
    ) -> ProjectState:
        self._guard_replacement(discard_unsaved)
        state = ProjectState.create(
            project_id,
            name,
            fps,
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
        )
        self._bus = CommandBus(state)
        self._session_id = uuid4().hex
        self._current_path = None
        self._saved_hash = None
        return state

    def open_project(self, path: Path, *, discard_unsaved: bool = False) -> ProjectState:
        self._guard_replacement(discard_unsaved)
        resolved = path.resolve()
        state = self.repository.load(resolved)
        # Compute the hash before replacing any active project session:
        # a malformed state from any repository must never install itself.
        saved_hash = state.semantic_hash()
        next_bus = CommandBus(state)
        self._bus = next_bus
        self._session_id = uuid4().hex
        self._current_path = resolved
        self._saved_hash = saved_hash
        return state

    def close(self, *, discard_unsaved: bool = False) -> None:
        self._guard_replacement(discard_unsaved)
        self._bus = None
        self._session_id = None
        self._current_path = None
        self._saved_hash = None

    def execute(self, batch: CommandBatch) -> ProjectState:
        return self.bus.execute(batch)

    def undo(self) -> ProjectState:
        return self.bus.undo()

    def redo(self) -> ProjectState:
        return self.bus.redo()

    def save(self, path: Path | None = None) -> Path:
        target = path.resolve() if path is not None else self._current_path
        if target is None:
            raise ProjectSessionError("Save requires a path for an unsaved project")
        # Fail before any file write if the current canonical state cannot
        # produce the identity used to decide whether the project is saved.
        state = self.state
        saved_hash = state.semantic_hash()
        self.repository.save(state, target)
        self._current_path = target
        self._saved_hash = saved_hash
        return target

    def save_as(self, path: Path) -> Path:
        return self.save(path)

    def recover_snapshot(
        self,
        source_path: Path,
        snapshot_path: Path,
        *,
        discard_unsaved: bool = False,
    ) -> ProjectState:
        """Adopt validated snapshot as dirty working state; never write source."""
        self._guard_replacement(discard_unsaved)
        source = source_path.resolve()
        original = self.repository.load(source)
        restored = self.repository.load(snapshot_path.resolve())
        original.validate()
        restored.validate()
        if original.project_id != restored.project_id:
            raise ProjectSessionError("recovery snapshot project mismatch")
        if restored.revision < original.revision:
            raise ProjectSessionError("recovery snapshot is older than source")
        # A custom repository may return domain-valid state containing invalid
        # Unicode. Hash before accepting recovery, just as open_project does.
        original.semantic_hash()
        restored.semantic_hash()
        next_bus = CommandBus(restored)
        self._bus = next_bus
        self._session_id = uuid4().hex
        self._current_path = source
        # Force dirty even for an identical semantic state: explicit Save is mandatory.
        self._saved_hash = None
        return restored

    def autosave(self, snapshot_dir: Path | None = None) -> Path:
        state = self.state
        if snapshot_dir is None:
            if self._current_path is None:
                raise ProjectSessionError("unsaved project autosave requires snapshot_dir")
            snapshot_dir = self._current_path.parent / ".ang-autosave"
        return self.autosave_catalog.create_snapshot(
            state, snapshot_dir, source_path=self._current_path
        )
