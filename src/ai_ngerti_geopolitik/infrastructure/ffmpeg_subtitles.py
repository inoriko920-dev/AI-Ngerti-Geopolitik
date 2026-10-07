"""Render-qualified W5 subtitle style projection for FFmpeg drawtext.

FFmpeg remains a qualification adapter behind MediaEnginePort. This module
proves canonical W5 subtitle style behavior without changing the production
engine priority decision.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import ProjectState, SubtitleCue, SubtitleStyle

QUALIFIED_FONT_FILES: dict[str, str] = {
    "Arial": "C\\:/Windows/Fonts/arial.ttf",
    "Segoe UI": "C\\:/Windows/Fonts/segoeui.ttf",
}


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace("%", "\\%")
        .replace("\r", "")
        .replace("\n", "\\n")
    )


def _fontfile(style: SubtitleStyle) -> str:
    try:
        return QUALIFIED_FONT_FILES[style.font_family]
    except KeyError as exc:
        supported = ", ".join(sorted(QUALIFIED_FONT_FILES))
        raise ValueError(
            f"subtitle font family is not render-qualified: {style.font_family}; "
            f"supported: {supported}"
        ) from exc


def _position(style: SubtitleStyle) -> tuple[str, str]:
    x = "(w-text_w)/2"
    if style.alignment == "top_center":
        y = str(style.margin_v)
    elif style.alignment == "center":
        y = "(h-text_h)/2"
    else:
        y = f"h-text_h-{style.margin_v}"
    return x, y


def _drawtext(cue: SubtitleCue, style: SubtitleStyle, *, enabled_window: bool) -> str:
    x, y = _position(style)
    border = max(0, round(style.outline_width_tenths / 10))
    shadow = max(0, round(style.shadow_tenths / 10))
    parts = [
        "drawtext",
        f"fontfile='{_fontfile(style)}'",
        f"text='{_escape_text(cue.text)}'",
        "expansion=none",
        f"fontsize={style.font_size}",
        f"fontcolor=0x{style.fill_color.lstrip('#')}",
        f"bordercolor=0x{style.outline_color.lstrip('#')}",
        f"borderw={border}",
        "shadowcolor=black@0.75",
        f"shadowx={shadow}",
        f"shadowy={shadow}",
        f"x='{x}'",
        f"y='{y}'",
    ]
    if style.background_box:
        parts.extend(
            [
                "box=1",
                f"boxcolor=black@{_number(style.background_opacity_percent / 100.0)}",
                "boxborderw=14",
            ]
        )
    else:
        parts.append("box=0")

    if enabled_window:
        start = cue.start.frames / cue.start.fps
        end = cue.end.frames / cue.end.fps
        parts.append(f"enable='between(t,{_number(start)},{_number(end)})'")
    return ":".join(parts)


@dataclass(frozen=True, slots=True)
class SubtitleRenderPlan:
    filters: tuple[str, ...]


def build_subtitle_preview_plan(
    state: ProjectState,
    timeline_frame: int,
) -> SubtitleRenderPlan:
    subtitle = state.subtitle
    if subtitle is None or not subtitle.enabled:
        return SubtitleRenderPlan(())
    active = next(
        (
            cue
            for cue in subtitle.cues
            if cue.start.frames <= timeline_frame < cue.end.frames
        ),
        None,
    )
    if active is None:
        return SubtitleRenderPlan(())
    return SubtitleRenderPlan((_drawtext(active, subtitle.style, enabled_window=False),))


def build_subtitle_export_plan(state: ProjectState) -> SubtitleRenderPlan:
    subtitle = state.subtitle
    if subtitle is None or not subtitle.enabled:
        return SubtitleRenderPlan(())
    return SubtitleRenderPlan(
        tuple(
            _drawtext(cue, subtitle.style, enabled_window=True)
            for cue in subtitle.cues
        )
    )
