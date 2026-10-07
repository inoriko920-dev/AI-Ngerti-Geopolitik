import json
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    SetNarrationTrackCommand,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    DomainValidationError,
    FrameTime,
    NarrationTrack,
    ProjectState,
    SubtitleAnimation,
    SubtitleCue,
    SubtitleStyle,
    SubtitleTrack,
    Track,
    WordTiming,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _base_state() -> ProjectState:
    video = Asset(
        "A001",
        "video.mp4",
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    narration = Asset(
        "A002",
        "narration.wav",
        "audio",
        FrameTime(240, 30),
        0,
        0,
        True,
        "b" * 64,
        sample_rate=48000,
    )
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(180, 30),
    )
    state = ProjectState(
        project_id="P-W5-001",
        name="W5 canonical",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(video, narration),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
    )
    state.validate()
    return state


def _subtitle() -> SubtitleTrack:
    return SubtitleTrack(
        source_ref="subtitle.srt",
        cues=(
            SubtitleCue(
                "SC001",
                1,
                FrameTime(0, 30),
                FrameTime(60, 30),
                "Baris pertama",
                (
                    WordTiming(
                        "W001",
                        "Baris",
                        FrameTime(0, 30),
                        FrameTime(30, 30),
                    ),
                    WordTiming(
                        "W002",
                        "pertama",
                        FrameTime(30, 30),
                        FrameTime(60, 30),
                    ),
                ),
            ),
            SubtitleCue(
                "SC002",
                2,
                FrameTime(60, 30),
                FrameTime(120, 30),
                "Baris kedua",
            ),
        ),
        style=SubtitleStyle(),
        animation=SubtitleAnimation(),
    )


def _narration() -> NarrationTrack:
    return NarrationTrack(
        narration_id="N001",
        asset_id="A002",
        timeline_start=FrameTime(0, 30),
        gain_percent=100,
        fade_in_frames=6,
        fade_out_frames=6,
    )


def test_w5_001_state_history_and_persistence_roundtrip(tmp_path: Path) -> None:
    bus = CommandBus(_base_state())
    baseline = bus.state.semantic_hash()

    bus.execute(
        CommandBatch(
            "W5-001-B1",
            "Bind canonical subtitle and narration",
            "manual",
            bus.state.revision,
            (
                SetSubtitleTrackCommand(_subtitle()),
                SetNarrationTrackCommand(_narration()),
            ),
        )
    )

    edited = bus.state.semantic_hash()
    assert edited != baseline
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.cues[0].word_timings[1].word == "pertama"
    assert bus.state.narration is not None
    assert bus.state.narration.asset_id == "A002"

    bus.undo()
    assert bus.state.semantic_hash() == baseline
    bus.redo()
    assert bus.state.semantic_hash() == edited

    path = tmp_path / "w5-001.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, path)
    loaded = repository.load(path)

    assert loaded.semantic_hash() == edited
    assert loaded.subtitle == bus.state.subtitle
    assert loaded.narration == bus.state.narration


def test_w5_001_legacy_project_without_new_fields_loads_safe_defaults(
    tmp_path: Path,
) -> None:
    repository = JsonProjectRepository()
    path = tmp_path / "legacy-w4.angproj"
    repository.save(_base_state(), path)

    raw = json.loads(path.read_text(encoding="utf-8"))
    raw.pop("subtitle", None)
    raw.pop("narration", None)
    path.write_text(json.dumps(raw), encoding="utf-8")

    loaded = repository.load(path)
    assert loaded.schema_version == 1
    assert loaded.subtitle is None
    assert loaded.narration is None


def test_w5_001_rejects_invalid_cue_and_word_timing() -> None:
    with pytest.raises(DomainValidationError, match="end must be after start"):
        SubtitleCue(
            "BAD",
            1,
            FrameTime(20, 30),
            FrameTime(20, 30),
            "invalid",
        )

    with pytest.raises(DomainValidationError, match="inside cue"):
        SubtitleCue(
            "BAD-WORD",
            1,
            FrameTime(30, 30),
            FrameTime(60, 30),
            "dua kata",
            (
                WordTiming(
                    "W1",
                    "dua",
                    FrameTime(0, 30),
                    FrameTime(40, 30),
                ),
            ),
        )


def test_w5_001_rejects_overlapping_subtitle_cues() -> None:
    with pytest.raises(DomainValidationError, match="overlapping subtitle cues"):
        SubtitleTrack(
            source_ref="overlap.srt",
            cues=(
                SubtitleCue(
                    "S1",
                    1,
                    FrameTime(0, 30),
                    FrameTime(60, 30),
                    "satu",
                ),
                SubtitleCue(
                    "S2",
                    2,
                    FrameTime(50, 30),
                    FrameTime(90, 30),
                    "dua",
                ),
            ),
        )


def test_w5_001_project_rejects_subtitle_outside_timeline() -> None:
    state = _base_state()
    subtitle = SubtitleTrack(
        source_ref="late.srt",
        cues=(
            SubtitleCue(
                "S1",
                1,
                FrameTime(150, 30),
                FrameTime(181, 30),
                "melewati timeline",
            ),
        ),
    )
    with pytest.raises(DomainValidationError, match="inside the timeline"):
        ProjectState(
            project_id=state.project_id,
            name=state.name,
            schema_version=state.schema_version,
            fps=state.fps,
            revision=state.revision,
            assets=state.assets,
            tracks=state.tracks,
            subtitle=subtitle,
        ).validate()


def test_w5_001_narration_requires_canonical_audio_asset() -> None:
    state = _base_state()

    with pytest.raises(DomainValidationError, match="canonical asset"):
        ProjectState(
            project_id=state.project_id,
            name=state.name,
            schema_version=state.schema_version,
            fps=state.fps,
            revision=state.revision,
            assets=state.assets,
            tracks=state.tracks,
            narration=NarrationTrack(
                "N404",
                "MISSING",
                FrameTime(0, 30),
            ),
        ).validate()

    with pytest.raises(DomainValidationError, match="audio asset"):
        ProjectState(
            project_id=state.project_id,
            name=state.name,
            schema_version=state.schema_version,
            fps=state.fps,
            revision=state.revision,
            assets=state.assets,
            tracks=state.tracks,
            narration=NarrationTrack(
                "NVIDEO",
                "A001",
                FrameTime(0, 30),
            ),
        ).validate()


def test_w5_001_rejects_unqualified_subtitle_animation_names() -> None:
    with pytest.raises(DomainValidationError, match="unsupported or unqualified"):
        SubtitleAnimation(preset="Karaoke Highlight", enter_frames=8, exit_frames=8)
