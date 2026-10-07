"""Real FFmpeg qualification mapping for SF-STEP 11 W4 creative state."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import Clip


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def _effect_scale_floor(effect: str) -> float | None:
    if effect in {"Pop", "Stomp"}:
        return 0.85
    if effect == "Breathe":
        return 0.98
    return None


def _scale_factor(
    clip: Clip,
    duration: float,
    window: float,
) -> str | None:
    effects = clip.properties.effects
    enter_floor = _effect_scale_floor(effects.enter_effect)
    exit_floor = _effect_scale_floor(effects.exit_effect)
    if enter_floor is None and exit_floor is None:
        return None

    win = _number(window)
    exit_start = _number(max(0.0, duration - window))
    enter = None
    if enter_floor is not None:
        excursion = 1.0 - enter_floor
        enter = f"{enter_floor:.2f}+{excursion:.2f}*t/{win}"
    exit_expr = None
    if exit_floor is not None:
        excursion = 1.0 - exit_floor
        exit_expr = f"1-{excursion:.2f}*(t-{exit_start})/{win}"

    if enter is not None and exit_expr is not None:
        return f"if(lt(t,{win}),{enter},if(gt(t,{exit_start}),{exit_expr},1))"
    if enter is not None:
        return f"if(lt(t,{win}),{enter},1)"
    return f"if(gt(t,{exit_start}),{exit_expr},1)"


def _motion_term(
    effect: str,
    *,
    entering: bool,
    duration: float,
    window: float,
    intensity: float,
) -> tuple[str, str] | None:
    win = _number(window)
    if effect == "Tectonic":
        distance = 0.012 * intensity
        phase = "18.849556"
        if entering:
            expression = f"if(lt(t,{win}),cos((t/{win})*{phase})*(1-t/{win})*W*{distance:.6f},0)"
        else:
            start = _number(max(0.0, duration - window))
            expression = (
                f"if(gt(t,{start}),"
                f"cos(((t-{start})/{win})*{phase})*"
                f"((t-{start})/{win})*W*{distance:.6f},0)"
            )
        return "x", expression

    if effect == "Rise":
        axis = "y"
        dimension = "H"
        distance = 0.08 * intensity
    elif effect in {"Pan", "Drift"}:
        axis = "x"
        dimension = "W"
        distance = 0.06 * intensity
    else:
        return None

    amount = f"{dimension}*{distance:.6f}"
    if entering:
        return axis, (f"if(lt(t,{win}),(1-t/{win})*{amount},0)")
    start = _number(max(0.0, duration - window))
    return axis, (f"if(gt(t,{start}),((t-{start})/{win})*{amount},0)")


def _combine(base: str, terms: list[str]) -> str:
    if not terms:
        return base
    return f"({base})+" + "+".join(f"({term})" for term in terms)


def _drawtext_filter(clip: Clip) -> str | None:
    title = clip.properties.title
    if not title.enabled:
        return None
    text = (
        title.text.strip()
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace("%", "\\%")
        .replace("\n", " ")
        .replace("\r", " ")
    )
    if title.position == "top":
        y = "60"
    elif title.position == "center":
        y = "(h-text_h)/2"
    else:
        y = "h-text_h-80"
    alpha = title.background_opacity_percent / 100.0
    return (
        "drawtext="
        "fontfile='C\\:/Windows/Fonts/arial.ttf':"
        f"text='{text}':"
        f"fontsize={title.font_size}:"
        f"fontcolor=0x{title.color_hex}:"
        "x=(w-text_w)/2:"
        f"y={y}:"
        "box=1:"
        f"boxcolor=black@{_number(alpha)}:"
        "boxborderw=14"
    )


@dataclass(frozen=True, slots=True)
class W4CreativePlan:
    source_filters: tuple[str, ...]
    overlay_x: str
    overlay_y: str
    post_filters: tuple[str, ...]


def build_w4_creative_plan(
    clip: Clip,
    fps: int,
    *,
    base_x: str,
    base_y: str,
) -> W4CreativePlan:
    if fps <= 0:
        raise ValueError("fps must be positive")

    effects = clip.properties.effects
    duration = clip.duration_frames / fps
    window = min(0.25, duration / 2.0)
    intensity = max(
        0.0,
        min(2.0, effects.intensity_percent / 100.0),
    )
    source_filters: list[str] = []

    if effects.enter_effect == "Fade" or effects.exit_effect == "Fade":
        source_filters.append("format=rgba")
        if effects.enter_effect == "Fade":
            source_filters.append(f"fade=t=in:st=0:d={_number(window)}:alpha=1")
        if effects.exit_effect == "Fade":
            start = max(0.0, duration - window)
            source_filters.append(f"fade=t=out:st={_number(start)}:d={_number(window)}:alpha=1")

    factor = _scale_factor(clip, duration, window)
    if factor is not None:
        source_filters.append(f"scale=w='max(2,trunc(iw*({factor})/2)*2)':h=-2:eval=frame")

    if effects.enter_effect == "Tumble" or effects.exit_effect == "Tumble":
        max_angle = 0.209440 * intensity
        terms: list[str] = []
        win = _number(window)
        if effects.enter_effect == "Tumble":
            terms.append(f"if(lt(t,{win}),-(1-t/{win})*{max_angle:.6f},0)")
        if effects.exit_effect == "Tumble":
            tumble_start = _number(max(0.0, duration - window))
            terms.append(f"if(gt(t,{tumble_start}),((t-{tumble_start})/{win})*{max_angle:.6f},0)")
        angle = "+".join(f"({term})" for term in terms)
        source_filters.append(f"rotate=a='{angle}':ow=iw:oh=ih:c=none")

    x_terms: list[str] = []
    y_terms: list[str] = []
    for effect, entering in (
        (effects.enter_effect, True),
        (effects.exit_effect, False),
    ):
        compiled = _motion_term(
            effect,
            entering=entering,
            duration=duration,
            window=window,
            intensity=intensity,
        )
        if compiled is None:
            continue
        axis, expression = compiled
        if axis == "x":
            x_terms.append(expression)
        else:
            y_terms.append(expression)

    post_filters: list[str] = []
    title_filter = _drawtext_filter(clip)
    if title_filter is not None:
        post_filters.append(title_filter)

    transition = clip.properties.transition
    if transition.preset == "fade_black":
        transition_seconds = min(
            transition.duration_frames / fps,
            max(1.0 / fps, duration / 2.0),
        )
        post_filters.append(f"fade=t=in:st=0:d={_number(transition_seconds)}:color=black")
        start = max(0.0, duration - transition_seconds)
        post_filters.append(
            f"fade=t=out:st={_number(start)}:d={_number(transition_seconds)}:color=black"
        )

    return W4CreativePlan(
        source_filters=tuple(source_filters),
        overlay_x=_combine(base_x, x_terms),
        overlay_y=_combine(base_y, y_terms),
        post_filters=tuple(post_filters),
    )
