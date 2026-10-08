"""W8-005 validated autosave catalog and bounded, project-scoped retention.

Only direct, correctly named, repository-validated snapshots are prune eligible.
Corrupt files, foreign projects, source projects and .bak are never deleted.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import ProjectRepositoryPort
from ai_ngerti_geopolitik.domain import ProjectState


class AutosaveCatalogError(RuntimeError):
    """Typed safe failure with no private project content in the message."""


@dataclass(frozen=True, slots=True)
class AutosaveRecord:
    path: Path
    project_id: str
    revision: int
    semantic_hash: str
    file_sha256: str
    timestamp_ns: int
    legacy_filename: bool


@dataclass(frozen=True, slots=True)
class AutosaveCatalog:
    project_id: str
    recoverable: tuple[AutosaveRecord, ...]
    rejected: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class AutosaveRetentionResult:
    kept: tuple[AutosaveRecord, ...]
    deleted: tuple[Path, ...]
    rejected: tuple[Path, ...]


def _validate_id(project_id: str) -> None:
    if (
        not project_id
        or project_id in {".", ".."}
        or "/" in project_id
        or "\\" in project_id
        or "\0" in project_id
    ):
        raise AutosaveCatalogError("invalid project id for autosave catalog")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as reader:
        while block := reader.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


class AutosaveCatalogService:
    """Managed extension of the existing ProjectRepositoryPort snapshot writer."""

    def __init__(
        self, repository: ProjectRepositoryPort, *, retention_limit: int = 20
    ) -> None:
        if not 1 <= retention_limit <= 20:
            raise ValueError("managed autosave retention must be between 1 and 20")
        self.repository = repository
        self.retention_limit = retention_limit

    def inspect(self, folder: Path, project_id: str) -> AutosaveCatalog:
        _validate_id(project_id)
        if folder.is_symlink():
            raise AutosaveCatalogError("symlinked autosave directory is not allowed")
        if not folder.is_dir():
            return AutosaveCatalog(project_id, (), ())
        expression = re.compile(
            rf"^{re.escape(project_id)}\.r([0-9]{{6,}})\."
            r"([0-9a-f]{12})(?:\.([0-9]{8}T[0-9]{12}Z))?\.autosave\.angproj$"
        )
        valid: list[AutosaveRecord] = []
        rejected: list[Path] = []
        # Enumerate direct entries only: no recursive scan or foreign-directory pruning.
        for path in sorted(folder.iterdir(), key=lambda item: item.name):
            if not path.name.startswith(f"{project_id}."):
                continue
            if not path.name.endswith(".autosave.angproj"):
                continue
            if path.is_symlink() or not path.is_file():
                rejected.append(path)
                continue
            match = expression.fullmatch(path.name)
            if match is None:
                rejected.append(path)
                continue
            try:
                parsed_revision = int(match.group(1))
                saved = self.repository.load(path)
                saved.validate()
                if (
                    saved.project_id != project_id
                    or saved.revision != parsed_revision
                    or not saved.semantic_hash().startswith(match.group(2))
                ):
                    rejected.append(path)
                    continue
                # Timestamp comes from the filename for managed snapshots.
                # Legacy snapshots use filesystem mtime without any rewrite.
                timestamp_ns = path.stat().st_mtime_ns
                if match.group(3) is not None:
                    moment = datetime.strptime(match.group(3), "%Y%m%dT%H%M%S%fZ")
                    timestamp_ns = int(moment.replace(tzinfo=UTC).timestamp() * 1_000_000_000)
                valid.append(
                    AutosaveRecord(
                        path=path,
                        project_id=project_id,
                        revision=saved.revision,
                        semantic_hash=saved.semantic_hash(),
                        file_sha256=_sha256(path),
                        timestamp_ns=timestamp_ns,
                        legacy_filename=match.group(3) is None,
                    )
                )
            except (OSError, RuntimeError, ValueError):
                rejected.append(path)
        valid.sort(key=lambda item: (-item.timestamp_ns, -item.revision, item.path.name))
        return AutosaveCatalog(project_id, tuple(valid), tuple(rejected))

    def enforce_retention(
        self,
        folder: Path,
        project_id: str,
        *,
        source_path: Path | None = None,
        protect: Path | None = None,
    ) -> AutosaveRetentionResult:
        catalog = self.inspect(folder, project_id)
        source = source_path.resolve() if source_path is not None else None
        protected_paths = {protect.resolve()} if protect is not None else set()
        if source is not None:
            protected_paths.add(source)
            protected_paths.add(source.with_name(f"{source.name}.bak"))
        kept: list[AutosaveRecord] = []
        deleted: list[Path] = []
        for record in catalog.recoverable:
            # Retain any explicitly protected snapshot without counting it as prunable.
            if len(kept) < self.retention_limit or record.path.resolve() in protected_paths:
                kept.append(record)
                continue
            # Defensive re-check: race, symlink swap or invalid content means NO unlink.
            if record.path.is_symlink() or record.path.parent.resolve() != folder.resolve():
                continue
            try:
                current = record.path.stat()
                if not current.is_file():
                    continue
                if _sha256(record.path) != record.file_sha256:
                    continue
                record.path.unlink()
                deleted.append(record.path)
            except OSError as exc:
                raise AutosaveCatalogError("unable to prune a validated autosave") from exc
        return AutosaveRetentionResult(tuple(kept), tuple(deleted), catalog.rejected)

    def create_snapshot(
        self,
        state: ProjectState,
        folder: Path,
        *,
        source_path: Path | None = None,
    ) -> Path:
        _validate_id(state.project_id)
        state.validate()
        if folder.is_symlink():
            raise AutosaveCatalogError("symlinked autosave directory is not allowed")
        folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        target = folder / (
            f"{state.project_id}.r{state.revision:06d}."
            f"{state.semantic_hash()[:12]}.{timestamp}.autosave.angproj"
        )
        if source_path is not None:
            source = source_path.resolve()
            if target.resolve() in {source, source.with_name(f"{source.name}.bak")}:
                raise AutosaveCatalogError("autosave may not overwrite the project source")
        # The repository remains the only persistence owner.
        self.repository.save_snapshot(state, target)
        catalog = self.inspect(folder, state.project_id)
        if not any(entry.path == target for entry in catalog.recoverable):
            raise AutosaveCatalogError("written snapshot failed catalog validation")
        self.enforce_retention(
            folder, state.project_id, source_path=source_path, protect=target
        )
        return target
