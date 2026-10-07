from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    CommandError,
    SetSubtitleAnimationCommand,
    SetSubtitleCueWordTimingsCommand,
)
from ai_ngerti_geopolitik.application.subtitle_word_timing import (
    NOT_SPEECH_ALIGNMENT_LABEL,
    WordTimingBoundaryError,
    evenly_distribute_words_not_speech_alignment,
)
from ai_ngerti_geopolitik.domain import (
    SUPPORTED_SUBTITLE_ANIMATIONS,
    UNSUPPORTED_SUBTITLE_ANIMATIONS,
    Asset,
    Clip,
    DomainValidationError,
    FrameTime,
    ProjectState,
    SubtitleAnimation,
    SubtitleCue,
    SubtitleTrack,
    Track,
    WordTiming,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_subtitles import (
    build_subtitle_export_plan,
    build_subtitle_preview_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _state(*, with_subtitle: bool = True) -> ProjectState:
    asset = Asset(
        "A001",
        "video.mp4",
        "video",
        FrameTime(240, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(180, 30),
    )
    subtitle = None
    if with_subtitle:
        subtitle = SubtitleTrack(
            "source.srt",
            (
                SubtitleCue(
                    "S001",
                    1,
                    FrameTime(30, 30),
                    FrameTime(120, 30),
                    "AI ngerti geopolitik",
                ),
            ),
        )
    state = ProjectState(
        project_id="P-W5-005",
        name="Subtitle animation",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
        subtitle=subtitle,
    )
    state.validate()
    return state


def _animation(preset: str) -> SubtitleAnimation:
    timing = 30 if preset == "Clean Documentary" else 18
    return SubtitleAnimation(
        preset=preset,
        enter_frames=timing,
        exit_frames=timing,
        intensity_percent=120,
    )


def test_only_render_qualified_animation_names_are_canonical() -> None:
    assert SUPPORTED_SUBTITLE_ANIMATIONS == (
        "none",
        "Fade",
        "Pop",
        "Slide Up",
        "Clean Documentary",
    )
    assert "Karaoke Highlight" in UNSUPPORTED_SUBTITLE_ANIMATIONS
    for preset in SUPPORTED_SUBTITLE_ANIMATIONS[1:]:
        assert (
            SubtitleAnimation(
                preset=preset,
                enter_frames=12,
                exit_frames=12,
            ).preset
            == preset
        )

    for preset in UNSUPPORTED_SUBTITLE_ANIMATIONS:
        with pytest.raises(DomainValidationError, match="unsupported or unqualified"):
            SubtitleAnimation(preset=preset, enter_frames=12, exit_frames=12)


def test_animation_command_history_and_persistence(tmp_path: Path) -> None:
    bus = CommandBus(_state())
    baseline = bus.state.semantic_hash()
    animation = _animation("Slide Up")
    bus.execute(
        CommandBatch(
            "W5-005-ANIM",
            "Set subtitle animation",
            "manual",
            bus.state.revision,
            (SetSubtitleAnimationCommand(animation),),
        )
    )
    animated = bus.state.semantic_hash()
    assert animated != baseline
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.animation == animation

    bus.undo()
    assert bus.state.semantic_hash() == baseline
    bus.redo()
    assert bus.state.semantic_hash() == animated

    path = tmp_path / "animated.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, path)
    loaded = repository.load(path)
    assert loaded.subtitle is not None
    assert loaded.subtitle.animation == animation
    assert loaded.semantic_hash() == animated


def test_animation_requires_bound_subtitle_and_fits_every_cue() -> None:
    with pytest.raises(CommandError, match="bound subtitle"):
        SetSubtitleAnimationCommand(_animation("Fade")).apply(_state(with_subtitle=False))

    too_long = SubtitleAnimation(
        preset="Fade",
        enter_frames=50,
        exit_frames=50,
    )
    with pytest.raises(DomainValidationError, match="fit every subtitle cue"):
        SetSubtitleAnimationCommand(too_long).apply(_state())


def test_each_qualified_animation_compiles_distinct_render_behavior() -> None:
    state = _state()
    baseline = build_subtitle_preview_plan(state, 36).filters[0]

    rendered: dict[str, str] = {}
    for preset in SUPPORTED_SUBTITLE_ANIMATIONS[1:]:
        animated = SetSubtitleAnimationCommand(_animation(preset)).apply(state)
        preview = build_subtitle_preview_plan(animated, 36).filters[0]
        export = build_subtitle_export_plan(animated).filters[0]
        assert "alpha=" in preview
        assert "alpha=" in export
        assert "enable='between(t,1,4)'" in export
        assert preview != baseline
        rendered[preset] = preview

    assert "fontsize=48" in rendered["Pop"]
    assert "+64" in rendered["Slide Up"]
    assert "+17.28" in rendered["Clean Documentary"]
    assert len(set(rendered.values())) == 4


def test_manual_word_timing_is_semantic_undoable_and_persistent(tmp_path: Path) -> None:
    bus = CommandBus(_state())
    assert bus.state.subtitle is not None
    cue = bus.state.subtitle.cues[0]
    timings = (
        WordTiming("W1", "AI", FrameTime(30, 30), FrameTime(50, 30)),
        WordTiming("W2", "ngerti", FrameTime(50, 30), FrameTime(80, 30)),
        WordTiming("W3", "geopolitik", FrameTime(80, 30), FrameTime(120, 30)),
    )
    baseline = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            "W5-005-WORD",
            "Set manual word timing",
            "manual",
            bus.state.revision,
            (SetSubtitleCueWordTimingsCommand(cue.cue_id, timings),),
        )
    )
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.cues[0].word_timings == timings
    word_hash = bus.state.semantic_hash()
    assert word_hash != baseline

    bus.undo()
    assert bus.state.semantic_hash() == baseline
    bus.redo()
    assert bus.state.semantic_hash() == word_hash

    path = tmp_path / "word-timing.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, path)
    loaded = repository.load(path)
    assert loaded.subtitle is not None
    assert loaded.subtitle.cues[0].word_timings == timings


def test_even_distribution_requires_explicit_not_speech_alignment_acknowledgement() -> None:
    state = _state()
    assert state.subtitle is not None
    cue = state.subtitle.cues[0]
    assert NOT_SPEECH_ALIGNMENT_LABEL == "NOT speech alignment"

    with pytest.raises(WordTimingBoundaryError, match="explicit acknowledgement"):
        evenly_distribute_words_not_speech_alignment(
            cue,
            acknowledge_not_speech_alignment=False,
        )

    timings = evenly_distribute_words_not_speech_alignment(
        cue,
        acknowledge_not_speech_alignment=True,
    )
    assert [item.word for item in timings] == ["AI", "ngerti", "geopolitik"]
    assert timings[0].start.frames == cue.start.frames
    assert timings[-1].end.frames == cue.end.frames
    assert all(item.end.frames > item.start.frames for item in timings)
