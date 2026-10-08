"""Atomic .angproj JSON persistence with W1 backup and W8-007 safe cleanup."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ai_ngerti_geopolitik.application.persistence_failure import (
    PersistenceError,
    PersistenceStage,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    AudioProperties,
    Clip,
    ClipProperties,
    ColorProperties,
    EffectProperties,
    FrameTime,
    Marker,
    NarrationTrack,
    ProjectSettings,
    ProjectState,
    SpeedProperties,
    SubtitleAnimation,
    SubtitleCue,
    SubtitleStyle,
    SubtitleTrack,
    TitleProperties,
    Track,
    TransitionProperties,
    VideoProperties,
    WordTiming,
)


class ProjectFormatError(RuntimeError):
    pass


def _strict_json_bool(value: object) -> bool:
    """Prevent malformed JSON strings/numbers from silently toggling project flags."""
    if type(value) is not bool:
        raise TypeError("expected JSON boolean")
    return value


class JsonProjectRepository:
    def save(self, state: ProjectState, path: Path) -> None:
        self._write(state, path, backup_existing=True)

    def save_snapshot(self, state: ProjectState, path: Path) -> None:
        self._write(state, path, backup_existing=False)

    def _write(self, state: ProjectState, path: Path, *, backup_existing: bool) -> None:
        state.validate()
        if path.suffix.lower() != ".angproj":
            raise ProjectFormatError("project file must use .angproj")
        data = state.semantic_dict(include_revision=True)
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

        stage = PersistenceStage.PREPARE
        temp_path: Path | None = None
        backup_temp: Path | None = None
        failed: PersistenceError | None = None
        cause: OSError | None = None
        try:
            path = path.resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            stage = PersistenceStage.TEMP_CREATE
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                # Register immediately: partial writes/fsync failures must not orphan .tmp.
                temp_path = Path(handle.name)
                stage = PersistenceStage.TEMP_WRITE
                handle.write(payload)
                handle.flush()
                stage = PersistenceStage.TEMP_SYNC
                os.fsync(handle.fileno())

            if backup_existing and path.exists():
                backup_path = path.with_name(f"{path.name}.bak")
                stage = PersistenceStage.BACKUP_CREATE
                with tempfile.NamedTemporaryFile(
                    "wb",
                    dir=path.parent,
                    prefix=f".{backup_path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as backup_handle:
                    backup_temp = Path(backup_handle.name)
                stage = PersistenceStage.BACKUP_COPY
                shutil.copy2(path, backup_temp)
                # Backup must be safely available before replacing the source.
                stage = PersistenceStage.BACKUP_REPLACE
                os.replace(backup_temp, backup_path)
                backup_temp = None

            stage = PersistenceStage.SOURCE_REPLACE
            os.replace(temp_path, path)
            temp_path = None
        except OSError as exc:
            failed = PersistenceError(stage)
            cause = exc
        finally:
            for leftover in (temp_path, backup_temp):
                if leftover is None:
                    continue
                try:
                    leftover.unlink(missing_ok=True)
                except OSError as exc:
                    # Do not mask the original failure with secondary cleanup errors.
                    if failed is None:
                        failed = PersistenceError(PersistenceStage.CLEANUP)
                        cause = exc
        if failed is not None:
            raise failed from cause

    def load(self, path: Path) -> ProjectState:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise TypeError("project root must be an object")
            return self._decode(raw)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
            IndexError,
            OverflowError,
            RecursionError,
        ):
            # Malformed nested JSON and unreadable files must fail as a typed,
            # privacy-safe load error. Never expose the user's path or parser
            # exception details through the UI or ordinary error logs.
            raise ProjectFormatError("invalid project file") from None

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
        assets = tuple(self._decode_asset(item) for item in raw.get("assets", []))
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
                    enabled=_strict_json_bool(clip.get("enabled", True)),
                    properties=self._decode_clip_properties(clip.get("properties")),
                )
                for clip in item.get("clips", [])
            )
            tracks.append(
                Track(
                    track_id=str(item["track_id"]),
                    kind=str(item["kind"]),
                    order=int(item["order"]),
                    clips=clips,
                    name=str(item.get("name", "")),
                    locked=_strict_json_bool(item.get("locked", False)),
                    muted=_strict_json_bool(item.get("muted", False)),
                    visible=_strict_json_bool(item.get("visible", True)),
                )
            )
        markers = tuple(
            Marker(
                marker_id=str(item["marker_id"]),
                frame=FrameTime(
                    int(item["frame"]["frames"]),
                    int(item["frame"]["fps"]),
                ),
                label=str(item["label"]),
                marker_type=str(item.get("marker_type", "marker")),
            )
            for item in raw.get("markers", [])
        )
        state = ProjectState(
            project_id=str(raw["project_id"]),
            name=str(raw["name"]),
            schema_version=int(raw["schema_version"]),
            fps=fps,
            revision=int(raw["revision"]),
            assets=assets,
            tracks=tuple(tracks),
            markers=markers,
            subtitle=self._decode_subtitle(raw.get("subtitle"), fps),
            narration=self._decode_narration(raw.get("narration"), fps),
            settings=settings,
        )
        state.validate()
        return state

    @staticmethod
    def _decode_subtitle(raw: object, fps: int) -> SubtitleTrack | None:
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise TypeError("subtitle must be an object")
        style_raw = raw.get("style", {})
        animation_raw = raw.get("animation", {})
        cues_raw = raw.get("cues", [])
        if not isinstance(style_raw, dict) or not isinstance(animation_raw, dict):
            raise TypeError("subtitle style/animation must be objects")
        if not isinstance(cues_raw, list):
            raise TypeError("subtitle cues must be a list")

        cues: list[SubtitleCue] = []
        for cue_raw in cues_raw:
            if not isinstance(cue_raw, dict):
                raise TypeError("subtitle cue must be an object")
            words_raw = cue_raw.get("word_timings", [])
            if not isinstance(words_raw, list):
                raise TypeError("subtitle word timings must be a list")
            words = tuple(
                WordTiming(
                    word_id=str(word["word_id"]),
                    word=str(word["word"]),
                    start=FrameTime(
                        int(word["start"]["frames"]),
                        int(word["start"].get("fps", fps)),
                    ),
                    end=FrameTime(
                        int(word["end"]["frames"]),
                        int(word["end"].get("fps", fps)),
                    ),
                )
                for word in words_raw
            )
            cues.append(
                SubtitleCue(
                    cue_id=str(cue_raw["cue_id"]),
                    index=int(cue_raw["index"]),
                    start=FrameTime(
                        int(cue_raw["start"]["frames"]),
                        int(cue_raw["start"].get("fps", fps)),
                    ),
                    end=FrameTime(
                        int(cue_raw["end"]["frames"]),
                        int(cue_raw["end"].get("fps", fps)),
                    ),
                    text=str(cue_raw["text"]),
                    word_timings=words,
                )
            )

        return SubtitleTrack(
            source_ref=str(raw["source_ref"]),
            cues=tuple(cues),
            style=SubtitleStyle(
                font_family=str(style_raw.get("font_family", "Arial")),
                font_size=int(style_raw.get("font_size", 54)),
                fill_color=str(style_raw.get("fill_color", "#FFFFFF")),
                outline_color=str(style_raw.get("outline_color", "#111111")),
                outline_width_tenths=int(style_raw.get("outline_width_tenths", 30)),
                shadow_tenths=int(style_raw.get("shadow_tenths", 10)),
                background_box=_strict_json_bool(style_raw.get("background_box", False)),
                background_opacity_percent=int(style_raw.get("background_opacity_percent", 0)),
                alignment=str(style_raw.get("alignment", "bottom_center")),
                margin_v=int(style_raw.get("margin_v", 64)),
            ),
            animation=SubtitleAnimation(
                preset=str(animation_raw.get("preset", "none")),
                enter_frames=int(animation_raw.get("enter_frames", 0)),
                exit_frames=int(animation_raw.get("exit_frames", 0)),
                intensity_percent=int(animation_raw.get("intensity_percent", 100)),
                highlight_color=str(animation_raw.get("highlight_color", "#FFD400")),
            ),
            enabled=_strict_json_bool(raw.get("enabled", True)),
        )

    @staticmethod
    def _decode_narration(raw: object, fps: int) -> NarrationTrack | None:
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise TypeError("narration must be an object")
        start_raw = raw.get("timeline_start")
        if not isinstance(start_raw, dict):
            raise TypeError("narration timeline_start must be an object")
        return NarrationTrack(
            narration_id=str(raw["narration_id"]),
            asset_id=str(raw["asset_id"]),
            timeline_start=FrameTime(
                int(start_raw["frames"]),
                int(start_raw.get("fps", fps)),
            ),
            gain_percent=int(raw.get("gain_percent", 100)),
            muted=_strict_json_bool(raw.get("muted", False)),
            fade_in_frames=int(raw.get("fade_in_frames", 0)),
            fade_out_frames=int(raw.get("fade_out_frames", 0)),
        )

    @staticmethod
    def _decode_clip_properties(raw: object) -> ClipProperties:
        if raw is None:
            return ClipProperties()
        if not isinstance(raw, dict):
            raise TypeError("clip properties must be an object")
        video_raw = raw.get("video", {})
        audio_raw = raw.get("audio", {})
        color_raw = raw.get("color", {})
        speed_raw = raw.get("speed", {})
        title_raw = raw.get("title", {})
        transition_raw = raw.get("transition", {})
        effects_raw = raw.get("effects", {})
        groups = (
            video_raw,
            audio_raw,
            color_raw,
            speed_raw,
            title_raw,
            transition_raw,
            effects_raw,
        )
        if not all(isinstance(item, dict) for item in groups):
            raise TypeError("clip property groups must be objects")
        return ClipProperties(
            video=VideoProperties(
                position_x=int(video_raw.get("position_x", 0)),
                position_y=int(video_raw.get("position_y", 0)),
                scale_x_percent=int(video_raw.get("scale_x_percent", 100)),
                scale_y_percent=int(video_raw.get("scale_y_percent", 100)),
                rotation_tenths=int(video_raw.get("rotation_tenths", 0)),
                opacity_percent=int(video_raw.get("opacity_percent", 100)),
                crop_left_percent=int(video_raw.get("crop_left_percent", 0)),
                crop_top_percent=int(video_raw.get("crop_top_percent", 0)),
                crop_right_percent=int(video_raw.get("crop_right_percent", 0)),
                crop_bottom_percent=int(video_raw.get("crop_bottom_percent", 0)),
            ),
            audio=AudioProperties(
                volume_percent=int(audio_raw.get("volume_percent", 100)),
                pan_percent=int(audio_raw.get("pan_percent", 0)),
                fade_in_frames=int(audio_raw.get("fade_in_frames", 0)),
                fade_out_frames=int(audio_raw.get("fade_out_frames", 0)),
            ),
            color=ColorProperties(
                brightness_percent=int(color_raw.get("brightness_percent", 0)),
                exposure_tenths_ev=int(color_raw.get("exposure_tenths_ev", 0)),
                contrast_percent=int(color_raw.get("contrast_percent", 0)),
                saturation_percent=int(color_raw.get("saturation_percent", 0)),
                temperature_percent=int(color_raw.get("temperature_percent", 0)),
                tint_percent=int(color_raw.get("tint_percent", 0)),
            ),
            speed=SpeedProperties(
                rate_percent=int(speed_raw.get("rate_percent", 100)),
            ),
            title=TitleProperties(
                enabled=_strict_json_bool(title_raw.get("enabled", False)),
                text=str(title_raw.get("text", "")),
                font_size=int(title_raw.get("font_size", 54)),
                position=str(title_raw.get("position", "bottom")),
                color_hex=str(title_raw.get("color_hex", "FFFFFF")),
                background_opacity_percent=int(title_raw.get("background_opacity_percent", 55)),
            ),
            transition=TransitionProperties(
                preset=str(transition_raw.get("preset", "none")),
                duration_frames=int(transition_raw.get("duration_frames", 0)),
            ),
            effects=EffectProperties(
                enter_effect=str(effects_raw.get("enter_effect", "None")),
                exit_effect=str(effects_raw.get("exit_effect", "None")),
                intensity_percent=int(effects_raw.get("intensity_percent", 100)),
                locked=_strict_json_bool(effects_raw.get("locked", False)),
            ),
        )

    @staticmethod
    def _decode_asset(item: dict[str, Any]) -> Asset:
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
            has_audio=_strict_json_bool(item["has_audio"]),
            fingerprint_sha256=str(item["fingerprint_sha256"]),
            source_name=str(item.get("source_name", Path(path_ref).name)),
            file_size=int(item.get("file_size", 0)),
            sample_rate=int(item.get("sample_rate", 0)),
            availability=str(item.get("availability", "online")),
        )
