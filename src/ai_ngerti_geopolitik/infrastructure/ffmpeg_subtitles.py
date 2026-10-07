"""Render-qualified W5 subtitle style and animation projection for FFmpeg drawtext.

FFmpeg remains a qualification adapter behind MediaEnginePort. This module
proves canonical W5 subtitle behavior without changing the production-engine
priority decision.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import (
    ProjectState,
    SubtitleAnimation,
    SubtitleCue,
    SubtitleStyle,
)

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


def _sample_envelope(
    cue: SubtitleCue,
    animation: SubtitleAnimation,
    timeline_frame: int,
) -> tuple[float, float]:
    elapsed = max(0, timeline_frame - cue.start.frames)
    remaining = max(0, cue.end.frames - timeline_frame)
    enter = min(1.0, elapsed / animation.enter_frames) if animation.enter_frames > 0 else 1.0
    exit_ = min(1.0, remaining / animation.exit_frames) if animation.exit_frames > 0 else 1.0
    return enter, exit_


def _dynamic_alpha(cue: SubtitleCue, animation: SubtitleAnimation) -> str | None:
    if animation.preset == "none":
        return None
    start = cue.start.frames / cue.start.fps
    end = cue.end.frames / cue.end.fps
    enter = animation.enter_frames / cue.start.fps
    exit_ = animation.exit_frames / cue.start.fps

    if animation.enter_frames and animation.exit_frames:
        enter_end = start + enter
        exit_start = end - exit_
        return (
            f"if(lt(t,{_number(enter_end)}),(t-{_number(start)})/{_number(enter)},"
            f"if(gt(t,{_number(exit_start)}),({_number(end)}-t)/{_number(exit_)},1))"
        )
    if animation.enter_frames:
        enter_end = start + enter
        return f"if(lt(t,{_number(enter_end)}),(t-{_number(start)})/{_number(enter)},1)"
    exit_start = end - exit_
    return f"if(gt(t,{_number(exit_start)}),({_number(end)}-t)/{_number(exit_)},1)"


def _sample_size_factor(
    animation: SubtitleAnimation,
    enter_progress: float,
) -> float:
    if animation.preset != "Pop":
        return 1.0
    excursion = 0.15 * (animation.intensity_percent / 100.0)
    return 1.0 - excursion * (1.0 - enter_progress)


def _dynamic_size(
    style: SubtitleStyle,
    cue: SubtitleCue,
    animation: SubtitleAnimation,
) -> str:
    if animation.preset != "Pop" or animation.enter_frames == 0:
        return str(style.font_size)
    start = cue.start.frames / cue.start.fps
    enter = animation.enter_frames / cue.start.fps
    enter_end = start + enter
    excursion = 0.15 * (animation.intensity_percent / 100.0)
    floor = 1.0 - excursion
    return (
        f"{style.font_size}*"
        f"if(lt(t,{_number(enter_end)}),"
        f"{_number(floor)}+{_number(excursion)}*(t-{_number(start)})/{_number(enter)},1)"
    )


def _motion_distance(animation: SubtitleAnimation) -> float:
    intensity = animation.intensity_percent / 100.0
    if animation.preset == "Slide Up":
        return 80.0 * intensity
    if animation.preset == "Clean Documentary":
        return 18.0 * intensity
    return 0.0


def _sample_y(
    base_y: str,
    animation: SubtitleAnimation,
    enter_progress: float,
) -> str:
    distance = _motion_distance(animation)
    if distance <= 0:
        return base_y
    offset = distance * (1.0 - enter_progress)
    return f"({base_y})+{_number(offset)}"


def _dynamic_y(
    base_y: str,
    cue: SubtitleCue,
    animation: SubtitleAnimation,
) -> str:
    distance = _motion_distance(animation)
    if distance <= 0 or animation.enter_frames == 0:
        return base_y
    start = cue.start.frames / cue.start.fps
    enter = animation.enter_frames / cue.start.fps
    enter_end = start + enter
    return (
        f"({base_y})+if(lt(t,{_number(enter_end)}),"
        f"{_number(distance)}*(1-(t-{_number(start)})/{_number(enter)}),0)"
    )


def _drawtext(
    cue: SubtitleCue,
    style: SubtitleStyle,
    animation: SubtitleAnimation,
    *,
    enabled_window: bool,
    sample_frame: int | None = None,
) -> str:
    x, base_y = _position(style)
    border = max(0, round(style.outline_width_tenths / 10))
    shadow = max(0, round(style.shadow_tenths / 10))

    alpha_value: str | None = None
    if sample_frame is not None:
        enter_progress, exit_progress = _sample_envelope(cue, animation, sample_frame)
        alpha = 1.0 if animation.preset == "none" else min(enter_progress, exit_progress)
        size = round(style.font_size * _sample_size_factor(animation, enter_progress))
        y = _sample_y(base_y, animation, enter_progress)
        alpha_value = _number(alpha)
        fontsize = str(max(1, size))
    else:
        fontsize = _dynamic_size(style, cue, animation)
        y = _dynamic_y(base_y, cue, animation)
        alpha_value = _dynamic_alpha(cue, animation)

    parts = [
        f"drawtext=fontfile='{_fontfile(style)}'",
        f"text='{_escape_text(cue.text)}'",
        "expansion=none",
        f"fontsize='{fontsize}'",
        f"fontcolor=0x{style.fill_color.lstrip('#')}",
        f"bordercolor=0x{style.outline_color.lstrip('#')}",
        f"borderw={border}",
        "shadowcolor=black@0.75",
        f"shadowx={shadow}",
        f"shadowy={shadow}",
        f"x='{x}'",
        f"y='{y}'",
    ]
    if alpha_value is not None:
        parts.append(f"alpha='{alpha_value}'")

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
        (cue for cue in subtitle.cues if cue.start.frames <= timeline_frame < cue.end.frames),
        None,
    )
    if active is None:
        return SubtitleRenderPlan(())
    return SubtitleRenderPlan(
        (
            _drawtext(
                active,
                subtitle.style,
                subtitle.animation,
                enabled_window=False,
                sample_frame=timeline_frame,
            ),
        )
    )


def build_subtitle_export_plan(state: ProjectState) -> SubtitleRenderPlan:
    subtitle = state.subtitle
    if subtitle is None or not subtitle.enabled:
        return SubtitleRenderPlan(())
    return SubtitleRenderPlan(
        tuple(
            _drawtext(
                cue,
                subtitle.style,
                subtitle.animation,
                enabled_window=True,
            )
            for cue in subtitle.cues
        )
    )
