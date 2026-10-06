"""Atomic .angproj JSON persistence with W1 backup and autosave support."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectSettings,
    ProjectState,
    Track,
)


class ProjectFormatError(RuntimeError):
    pass


class JsonProjectRepository:
    def save(self, state: ProjectState, path: Path) -> None:
        self._write(state, path, backup_existing=True)

    def save_snapshot(self, state: ProjectState, path: Path) -> None:
        self._write(state, path, backup_existing=False)

    def _write(self, state: ProjectState, path: Path, *, backup_existing: bool) -> None:
        state.validate()
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() != ".angproj":
            raise ProjectFormatError("project file must use .angproj")
        data = state.semantic_dict(include_revision=True)
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\\n"\n
        temp_path: Path | None = None
        backup_temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="\\n",\n                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
                temp_path = Path(handle.name)

            if backup_existing and path.exists():
                backup_path = path.with_name(f"{path.name}.bak")
                with tempfile.NamedTemporaryFile(
                    "wb",
                    dir=path.parent,
                    prefix=f".{backup_path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as backup_handle:
                    backup_temp = Path(backup_handle.name)
                shutil.copy2(path, backup_temp)
                os.replace(backup_temp, backup_path)
                backup_temp = None

            os.replace(temp_path, path)
            temp_path = None
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
            if backup_temp is not None and backup_temp.exists():
                backup_temp.unlink()

    def load(self, path: Path) -> ProjectState:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise TypeError("project root must be an object")
            return self._decode(raw)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ProjectFormatError(f"invalid project file: {path}") from exc

    def _decode(self, raw: dict[str, Any]) -> ProjectState:
        fps = int(raw["fps"])
        settings_raw = raw.get("settings", {})
        if not isinstance(settings_raw, dict):
            raise TypeError("settings must be an object")
        settings = ProjectSettings(
            width=int(settings_raw.get("width", 1920)),
            height=int(settings_raw.get("height", 1080)),
            aspect_ratio=str(settings_raw.get("aspect_ratio", "16:9")),
        )
        assets = tuple(self._decode_asset(item, fps) for item in raw.get("assets", []))
        tracks: list[Track] = []
        for item in raw.get("tracks", []):
            clips = tuple(
                Clip(
                    clip_id=str(clip["clip_id"]),
                    asset_id=str(clip["asset_id"]),
                    timeline_start=FrameTime(
                        int(clip["timeline_start"]["frames"]),
                        int(clip["timeline_start"]["fps"]),
                    ),
                    source_in=FrameTime(
                        int(clip["source_in"]["frames"]),
                        int(clip["source_in"]["fps"]),
                    ),
                    source_out=FrameTime(
                        int(clip["source_out"]["frames"]),
                        int(clip["source_out"]["fps"]),
                    ),
                    enabled=bool(clip.get("enabled", True)),
                )
                for clip in item.get("clips", [])
            )
            tracks.append(
                Track(
                    track_id=str(item["track_id"]),
                    kind=str(item["kind"]),
                    order=int(item["order"]),
                    clips=clips,
                )
            )
        state = ProjectState(
            project_id=str(raw["project_id"]),
            name=str(raw["name"]),
            schema_version=int(raw["schema_version"]),
            fps=fps,
            revision=int(raw["revision"]),
            assets=assets,
            tracks=tuple(tracks),
            settings=settings,
        )
        state.validate()
        return state

    @staticmethod
    def _decode_asset(item: dict[str, Any], _fps: int) -> Asset:
        path_ref = str(item["path_ref"])
        return Asset(
            asset_id=str(item["asset_id"]),
            path_ref=path_ref,
            media_type=str(item["media_type"]),
            duration=FrameTime(
                int(item["duration"]["frames"]),
                int(item["duration"]["fps"]),
            ),
            width=int(item["width"]),
            height=int(item["height"]),
            has_audio=bool(item["has_audio"]),
            fingerprint_sha256=str(item["fingerprint_sha256"]),
            source_name=str(item.get("source_name", Path(path_ref).name)),
            file_size=int(item.get("file_size", 0)),
            sample_rate=int(item.get("sample_rate", 0)),
            availability=str(item.get("availability", "online")),
        )
