"""Canonical still-image HOLD v1 regression and legacy media compatibility."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    CommandError,
    SetClipDurationCommand,
    SetClipSpeedCommand,
    SplitClipCommand,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    DomainValidationError,
    FrameTime,
    ProjectState,
    SpeedProperties,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.mlt_projection import (
    MltProjectionError,
    build_mlt_timeline_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


def _image(asset_id: str, fps: int = 30) -> Asset:
    return Asset(
        asset_id=asset_id,
        path_ref=f"/fixture/{asset_id}.png",
        media_type="image",
        duration=FrameTime(1, fps),
        width=640,
        height=360,
        has_audio=False,
        fingerprint_sha256="a" * 64,
        source_name=f"{asset_id}.png",
        file_size=321,
    )


def _clip(asset_id: str, start: int, hold: int, clip_id: str | None = None) -> Clip:
    return Clip(
        clip_id=clip_id or f"IMG-{asset_id}",
        asset_id=asset_id,
        timeline_start=FrameTime(start, 30),
        source_in=FrameTime(0, 30),
        source_out=FrameTime(1, 30),
        image_hold_frames=hold,
    )


def _still_project() -> ProjectState:
    state = ProjectState.create("P-IMAGE", "Valid image project", 30)
    state = replace(
        state,
        assets=(_image("A001"), _image("A002"), _image("A003")),
        tracks=(
            Track("V1", "video", 0, (_clip("A001", 0, 150), _clip("A002", 150, 90))),
            Track("V2", "video", 1, (_clip("A003", 150, 90),)),
        ),
    )
    state.validate()
    return state


def test_still_scenes_are_genuine_image_clips_and_roundtrip_exactly(tmp_path: Path) -> None:
    state = _still_project()
    assert state.timeline_end_frame == 240
    assert state.clip("IMG-A001").source_duration_frames == 1
    assert state.clip("IMG-A001").duration_frames == 150
    assert state.clip("IMG-A001").source_frame_at_timeline_offset(149) == 0
    repo = JsonProjectRepository()
    saved = tmp_path / "images.angproj"
    repo.save(state, saved)
    raw = json.loads(saved.read_text(encoding="utf-8"))
    assert raw["tracks"][0]["clips"][0]["image_hold_frames"] == 150
    assert raw["assets"][0]["media_type"] == "image"
    loaded = repo.load(saved)
    assert loaded.semantic_hash() == state.semantic_hash()
    assert loaded.timeline_end_frame == 240
    assert loaded.clip("IMG-A003").timeline_start.frames == 150


def test_legacy_video_project_json_and_hash_not_changed_by_optional_field(tmp_path: Path) -> None:
    fps = 30
    asset = Asset(
        "A001", "/fixture/video.mp4", "video", FrameTime(200, fps), 1920, 1080, True, "b" * 64
    )
    clip = Clip("VIDEO-001", "A001", FrameTime(0, fps), FrameTime(0, fps), FrameTime(100, fps))
    state = replace(
        ProjectState.create("P-LEGACY", "Video unchanged", fps),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )
    state.validate()
    doc = state.semantic_dict(include_revision=True)
    assert "image_hold_frames" not in doc["tracks"][0]["clips"][0]
    repo = JsonProjectRepository()
    path = tmp_path / "legacy.angproj"
    repo.save(state, path)
    loaded = repo.load(path)
    assert loaded.semantic_hash() == state.semantic_hash()
    assert loaded.clip("VIDEO-001").image_hold_frames is None
    assert "image_hold_frames" not in path.read_text(encoding="utf-8")
    assert build_mlt_timeline_plan(loaded).timeline_end_frame == 100


def test_image_clip_with_wrong_or_missing_hold_and_video_with_hold_rejected() -> None:
    state = _still_project()
    image = state.clip("IMG-A001")
    for bad in (None, 0, -1, True, "150", 86400 * 30 + 1):
        candidate = replace(image, image_hold_frames=bad)
        broken = replace(
            state,
            tracks=(
                replace(state.tracks[0], clips=(candidate, *state.tracks[0].clips[1:])),
                state.tracks[1],
            ),
        )
        with pytest.raises(DomainValidationError):
            broken.validate()
    video_asset = replace(state.assets[0], media_type="video", duration=FrameTime(200, 30))
    mixed = replace(state, assets=(video_asset, *state.assets[1:]))
    with pytest.raises(DomainValidationError, match="video clips cannot"):
        mixed.validate()
    image_source_wrong = replace(image, source_out=FrameTime(2, 30))
    mixed = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(image_source_wrong, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    with pytest.raises(DomainValidationError, match="intrinsic one frame"):
        mixed.validate()


@pytest.mark.parametrize("bad", [False, 0, -1, 1.5, "12", {}, []])
def test_invalid_persisted_image_hold_is_typed_safe_error(tmp_path: Path, bad: object) -> None:
    path = tmp_path / "project.angproj"
    JsonProjectRepository().save(_still_project(), path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["tracks"][0]["clips"][0]["image_hold_frames"] = bad
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ProjectFormatError, match="invalid project file"):
        JsonProjectRepository().load(path)


def test_image_timeline_remains_fail_closed_for_unqualified_mlt_backend() -> None:
    with pytest.raises(MltProjectionError, match="requires video assets"):
        build_mlt_timeline_plan(_still_project())


def test_image_hold_edit_split_trim_and_undo_redo_are_frame_accurate() -> None:
    original = replace(
        _still_project(),
        tracks=(Track("V1", "video", 0, (_clip("A001", 0, 150),)),),
    )
    bus = CommandBus(original)

    def run(command):
        return bus.execute(
            CommandBatch(
                f"EDIT-{bus.state.revision}", "image edit", "manual", bus.state.revision, (command,)
            )
        )

    state = run(SetClipDurationCommand("IMG-A001", 120))
    assert state.clip("IMG-A001").duration_frames == 120
    assert state.clip("IMG-A001").source_out.frames == 1
    assert bus.undo().clip("IMG-A001").duration_frames == 150
    assert bus.redo().clip("IMG-A001").duration_frames == 120
    state = run(SplitClipCommand("IMG-A001", 50, "IMG-RIGHT"))
    assert state.clip("IMG-A001").duration_frames == 50
    assert state.clip("IMG-RIGHT").duration_frames == 70
    assert state.clip("IMG-RIGHT").source_in.frames == 0
    assert state.clip("IMG-RIGHT").timeline_start.frames == 50
    state = run(TrimClipCommand("IMG-RIGHT", 10, edge="left"))
    assert state.clip("IMG-RIGHT").duration_frames == 60
    assert state.clip("IMG-RIGHT").timeline_start.frames == 60
    with pytest.raises(CommandError, match="independent"):
        run(SetClipSpeedCommand("IMG-RIGHT", 50))
    assert bus.state.clip("IMG-RIGHT").duration_frames == 60
