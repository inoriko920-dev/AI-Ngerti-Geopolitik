from __future__ import annotations

from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    NarrationTrack,
    ProjectState,
    SubtitleAnimation,
    SubtitleCue,
    SubtitleStyle,
    SubtitleTrack,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_narration import (
    build_narration_render_plan,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_subtitles import (
    build_subtitle_export_plan,
    build_subtitle_preview_plan,
)


def _combined_state(animation: str = "Slide Up") -> ProjectState:
    video = Asset(
        "A001",
        "video.mp4",
        "video",
        FrameTime(180, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    narration = Asset(
        "A002",
        "voice.wav",
        "audio",
        FrameTime(120, 30),
        0,
        0,
        True,
        "b" * 64,
        sample_rate=48000,
    )
    cue = SubtitleCue(
        "SRT-000001",
        1,
        FrameTime(45, 30),
        FrameTime(135, 30),
        "EDITED COMBINED W5-009",
    )
    subtitle = SubtitleTrack(
        "edited.srt",
        (cue,),
        style=SubtitleStyle(
            font_family="Segoe UI",
            font_size=80,
            fill_color="#FFD166",
            outline_color="#003049",
            outline_width_tenths=50,
            shadow_tenths=30,
            background_box=True,
            background_opacity_percent=60,
            alignment="top_center",
            margin_v=90,
        ),
        animation=SubtitleAnimation(
            preset=animation,
            enter_frames=18 if animation != "Clean Documentary" else 30,
            exit_frames=18 if animation != "Clean Documentary" else 30,
            intensity_percent=120,
        ),
    )
    state = ProjectState(
        project_id="P-W5-009",
        name="Combined qualification",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(video, narration),
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
        subtitle=subtitle,
        narration=NarrationTrack(
            "N001",
            "A002",
            FrameTime(60, 30),
            gain_percent=80,
            fade_in_frames=15,
            fade_out_frames=15,
        ),
    )
    state.validate()
    return state


def test_combined_state_compiles_subtitle_and_narration_together() -> None:
    state = _combined_state()
    subtitle = build_subtitle_export_plan(state)
    narration = build_narration_render_plan(state)

    assert len(subtitle.filters) == 1
    assert "EDITED COMBINED W5-009" in subtitle.filters[0]
    assert "segoeui.ttf" in subtitle.filters[0]
    assert "enable='between(t,1.5,4.5)'" in subtitle.filters[0]
    assert narration is not None
    assert "volume=0.8" in narration.filters
    assert "adelay=2000:all=1" in narration.filters


def test_edited_subtitle_timing_is_active_only_inside_canonical_range() -> None:
    state = _combined_state()
    assert build_subtitle_preview_plan(state, 44).filters == ()
    assert len(build_subtitle_preview_plan(state, 45).filters) == 1
    assert len(build_subtitle_preview_plan(state, 90).filters) == 1
    assert build_subtitle_preview_plan(state, 135).filters == ()


def test_all_ui_enabled_animation_presets_compile_with_combined_state() -> None:
    for preset in ("Fade", "Pop", "Slide Up", "Clean Documentary"):
        state = _combined_state(preset)
        preview = build_subtitle_preview_plan(state, 51)
        export = build_subtitle_export_plan(state)
        narration = build_narration_render_plan(state)
        assert preview.filters
        assert export.filters
        assert narration is not None
