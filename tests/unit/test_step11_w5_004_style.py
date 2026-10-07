from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    CommandError,
    SetSubtitleStyleCommand,
)
from ai_ngerti_geopolitik.application.subtitle_working_copy import (
    SubtitleWorkingCopy,
    SubtitleWorkingCopyService,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectState,
    SubtitleCue,
    SubtitleStyle,
    SubtitleTrack,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_subtitles import (
    build_subtitle_export_plan,
    build_subtitle_preview_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser, Utf8SrtWriter


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
            source_ref="source.srt",
            cues=(
                SubtitleCue(
                    "S001",
                    1,
                    FrameTime(30, 30),
                    FrameTime(90, 30),
                    "Styled subtitle",
                ),
            ),
        )
    state = ProjectState(
        project_id="P-W5-004",
        name="Subtitle style",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
        subtitle=subtitle,
    )
    state.validate()
    return state


def _style() -> SubtitleStyle:
    return SubtitleStyle(
        font_family="Segoe UI",
        font_size=78,
        fill_color="#FFD166",
        outline_color="#003049",
        outline_width_tenths=50,
        shadow_tenths=30,
        background_box=True,
        background_opacity_percent=65,
        alignment="top_center",
        margin_v=90,
    )


def test_style_command_requires_bound_subtitle() -> None:
    with pytest.raises(CommandError, match="bound subtitle"):
        SetSubtitleStyleCommand(_style()).apply(_state(with_subtitle=False))


def test_style_command_undo_redo_and_persistence(tmp_path: Path) -> None:
    bus = CommandBus(_state())
    baseline = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            "W5-004-STYLE",
            "Set subtitle style",
            "manual",
            bus.state.revision,
            (SetSubtitleStyleCommand(_style()),),
        )
    )
    styled = bus.state.semantic_hash()
    assert styled != baseline
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.style == _style()

    bus.undo()
    assert bus.state.semantic_hash() == baseline
    bus.redo()
    assert bus.state.semantic_hash() == styled

    path = tmp_path / "styled.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, path)
    loaded = repository.load(path)
    assert loaded.subtitle is not None
    assert loaded.subtitle.style == _style()
    assert loaded.semantic_hash() == styled


def test_render_plan_covers_frozen_style_surface() -> None:
    state = SetSubtitleStyleCommand(_style()).apply(_state())
    preview = build_subtitle_preview_plan(state, 45)
    assert len(preview.filters) == 1
    rendered = preview.filters[0]

    assert "segoeui.ttf" in rendered
    assert "fontsize=78" in rendered
    assert "fontcolor=0xFFD166" in rendered
    assert "bordercolor=0x003049" in rendered
    assert "borderw=5" in rendered
    assert "shadowx=3" in rendered and "shadowy=3" in rendered
    assert "box=1" in rendered
    assert "boxcolor=black@0.65" in rendered
    assert "y='90'" in rendered

    export = build_subtitle_export_plan(state)
    assert len(export.filters) == 1
    assert "enable='between(t,1,3)'" in export.filters[0]


def test_preview_plan_only_renders_active_cue() -> None:
    state = _state()
    assert build_subtitle_preview_plan(state, 0).filters == ()
    assert len(build_subtitle_preview_plan(state, 30).filters) == 1
    assert build_subtitle_preview_plan(state, 90).filters == ()


def test_unqualified_font_is_explicitly_rejected() -> None:
    state = SetSubtitleStyleCommand(
        SubtitleStyle(font_family="Unqualified Font")
    ).apply(_state())
    with pytest.raises(ValueError, match="not render-qualified"):
        build_subtitle_preview_plan(state, 45)


def test_save_copy_preserves_latest_project_style_while_working_copy_is_dirty(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.srt"
    source.write_text(
        "1\n00:00:01,000 --> 00:00:03,000\nOriginal\n",
        encoding="utf-8",
    )
    state = _state()
    assert state.subtitle is not None
    state = ProjectState(
        project_id=state.project_id,
        name=state.name,
        schema_version=state.schema_version,
        fps=state.fps,
        revision=state.revision,
        assets=state.assets,
        tracks=state.tracks,
        subtitle=SubtitleTrack(
            source_ref=str(source.resolve()),
            cues=state.subtitle.cues,
        ),
        settings=state.settings,
    )
    bus = CommandBus(state)
    working = SubtitleWorkingCopy(bus.state.subtitle)
    working.edit_selected(text="Working copy edit")

    bus.execute(
        CommandBatch(
            "W5-004-LIVE-STYLE",
            "Style while cue working copy is dirty",
            "manual",
            bus.state.revision,
            (SetSubtitleStyleCommand(_style()),),
        )
    )

    output = SubtitleWorkingCopyService(Utf8SrtWriter()).save_copy_and_commit(
        bus,
        working,
    )
    assert output.is_file()
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.style == _style()
    assert bus.state.subtitle.cues[0].text == "Working copy edit"
    assert Utf8SrtParser().parse(output)[0].text == "Working copy edit"
