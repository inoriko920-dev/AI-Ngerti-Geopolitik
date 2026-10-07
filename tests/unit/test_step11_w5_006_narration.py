from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBatch, SetNarrationTrackCommand
from ai_ngerti_geopolitik.application.narration import (
    NarrationBindingError,
    NarrationImportService,
)
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    DomainValidationError,
    FrameTime,
    NarrationTrack,
    ProjectState,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_narration import (
    build_narration_render_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class Probe:
    def __init__(self, media_type: str = "audio") -> None:
        self.media_type = media_type

    def probe(self, path: Path) -> ProbeResult:
        if self.media_type == "audio":
            return ProbeResult(
                path=path.resolve(),
                duration_frames=0,
                fps=0,
                width=0,
                height=0,
                has_audio=True,
                fingerprint_sha256="b" * 64,
                media_type="audio",
                duration_seconds=4.0,
                file_size=100,
                sample_rate=48000,
            )
        return ProbeResult(
            path=path.resolve(),
            duration_frames=180,
            fps=30,
            width=1920,
            height=1080,
            has_audio=True,
            fingerprint_sha256="c" * 64,
            media_type="video",
            duration_seconds=6.0,
            file_size=100,
            sample_rate=48000,
        )


def _session() -> ProjectSession:
    state = ProjectState(
        project_id="P-W5-006",
        name="Narration",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(
            Asset(
                "A001",
                "video.mp4",
                "video",
                FrameTime(180, 30),
                1920,
                1080,
                True,
                "a" * 64,
            ),
        ),
        tracks=(
            Track(
                "V1",
                "video",
                0,
                (
                    Clip(
                        "C001",
                        "A001",
                        FrameTime(0, 30),
                        FrameTime(0, 30),
                        FrameTime(180, 30),
                    ),
                ),
                "Video 1",
            ),
        ),
    )
    state.validate()
    session = ProjectSession(JsonProjectRepository())
    session.new_project("TEMP", "Temp")
    session.bus.replace_loaded_state(state)
    return session


def test_import_and_bind_is_atomic_and_undoable(tmp_path: Path) -> None:
    session = _session()
    service = NarrationImportService(Probe())

    asset_id = service.import_and_bind(
        session,
        tmp_path / "narration.wav",
        timeline_start_frame=60,
        gain_percent=80,
        fade_in_frames=15,
        fade_out_frames=15,
    )
    assert asset_id == "A002"
    assert session.state.revision == 1
    assert session.state.asset("A002").media_type == "audio"
    assert session.state.narration is not None
    assert session.state.narration.asset_id == "A002"
    assert session.state.narration.timeline_start.frames == 60

    session.undo()
    assert session.state.narration is None
    with pytest.raises(DomainValidationError, match="unknown asset"):
        session.state.asset("A002")

    session.redo()
    assert session.state.narration is not None
    assert session.state.asset("A002").sample_rate == 48000


def test_non_audio_import_fails_without_mutating_project(tmp_path: Path) -> None:
    session = _session()
    baseline = session.state.semantic_hash()
    with pytest.raises(NarrationBindingError, match="must be an audio"):
        NarrationImportService(Probe("video")).import_and_bind(
            session,
            tmp_path / "not-audio.mp4",
        )
    assert session.state.semantic_hash() == baseline
    assert session.state.revision == 0
    assert len(session.state.assets) == 1


def test_narration_controls_persist_and_history_is_reversible(tmp_path: Path) -> None:
    session = _session()
    NarrationImportService(Probe()).import_and_bind(
        session,
        tmp_path / "voice.wav",
        timeline_start_frame=30,
    )
    assert session.state.narration is not None
    baseline = session.state.semantic_hash()
    edited = NarrationTrack(
        narration_id=session.state.narration.narration_id,
        asset_id=session.state.narration.asset_id,
        timeline_start=FrameTime(45, 30),
        gain_percent=175,
        muted=True,
        fade_in_frames=20,
        fade_out_frames=25,
    )
    session.execute(
        CommandBatch(
            "W5-006-CONTROLS",
            "Edit narration controls",
            "manual",
            session.state.revision,
            (SetNarrationTrackCommand(edited),),
        )
    )
    edited_hash = session.state.semantic_hash()
    assert edited_hash != baseline

    session.undo()
    assert session.state.semantic_hash() == baseline
    session.redo()
    assert session.state.semantic_hash() == edited_hash

    path = tmp_path / "narration.angproj"
    session.save(path)
    opened = ProjectSession(JsonProjectRepository())
    opened.open_project(path)
    assert opened.state.narration == edited


def test_narration_fades_must_fit_audible_timeline_segment(tmp_path: Path) -> None:
    session = _session()
    NarrationImportService(Probe()).import_and_bind(
        session,
        tmp_path / "voice.wav",
        timeline_start_frame=150,
    )
    assert session.state.narration is not None
    invalid = NarrationTrack(
        narration_id=session.state.narration.narration_id,
        asset_id=session.state.narration.asset_id,
        timeline_start=FrameTime(150, 30),
        fade_in_frames=20,
        fade_out_frames=20,
    )
    with pytest.raises(DomainValidationError, match="audible duration"):
        SetNarrationTrackCommand(invalid).apply(session.state)


def test_render_plan_proves_offset_gain_mute_and_fades(tmp_path: Path) -> None:
    session = _session()
    NarrationImportService(Probe()).import_and_bind(
        session,
        tmp_path / "voice.wav",
        timeline_start_frame=60,
        gain_percent=150,
        fade_in_frames=15,
        fade_out_frames=30,
    )
    plan = build_narration_render_plan(session.state)
    assert plan is not None
    assert plan.audible_frames == 120
    assert "volume=1.5" in plan.filters
    assert "afade=t=in:st=0:d=0.5" in plan.filters
    assert "afade=t=out:st=3:d=1" in plan.filters
    assert "adelay=2000:all=1" in plan.filters

    assert session.state.narration is not None
    muted = NarrationTrack(
        narration_id=session.state.narration.narration_id,
        asset_id=session.state.narration.asset_id,
        timeline_start=session.state.narration.timeline_start,
        gain_percent=150,
        muted=True,
        fade_in_frames=15,
        fade_out_frames=30,
    )
    muted_state = SetNarrationTrackCommand(muted).apply(session.state)
    muted_plan = build_narration_render_plan(muted_state)
    assert muted_plan is not None
    assert "volume=0" in muted_plan.filters
