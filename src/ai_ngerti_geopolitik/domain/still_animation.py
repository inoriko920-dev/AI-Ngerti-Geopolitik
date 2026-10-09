"""Frame-exact qualification for limited W4 still-image animation.

Native Pilot A can render a single active V1 image HOLD with one of:
- W4 fade-through-black transition;
- W4 Fade enter and/or Fade exit effect;
- W4 Pan enter and/or Pan exit effect (bounded horizontal motion);
- W4 Drift enter and/or Drift exit effect (bounded diagonal motion).
- W4 Rise enter and/or Rise exit effect (bounded vertical motion).
- W4 Breathe enter and/or exit (bounded 0.98–1.00 centered scale).
All use canonical clip duration. Unsupported combinations fail closed.
"""

from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.domain.project import Clip
from ai_ngerti_geopolitik.domain.properties import (
    ClipProperties,
    EffectProperties,
    TransitionProperties,
)


def qualified_still_pan(clip: Clip, timeline_frame: int) -> float | None:
    """Horizontal pan position from -1 (opening), 0 (center), to +1 (closing).

    A qualified W4 Pan always maintains a 12% overscan, so image boundaries
    never expose a black gap. The enter/exit window is the W4 0.25s rule.
    """
    if clip.properties == ClipProperties():
        return None
    props = clip.properties
    effects = props.effects
    qualified = (
        clip.image_hold_frames is not None
        and props.transition.preset == "none"
        and effects.enter_effect in {"None", "Pan"}
        and effects.exit_effect in {"None", "Pan"}
        and (effects.enter_effect == "Pan" or effects.exit_effect == "Pan")
        and effects.intensity_percent == 100
        and replace(props, effects=EffectProperties()) == ClipProperties()
    )
    if not qualified:
        return None
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("pan frame outside clip")
    window = max(1.0, min(0.25 * clip.timeline_start.fps, clip.duration_frames / 2.0))
    entering = -max(0.0, 1.0 - offset / window) if effects.enter_effect == "Pan" else 0.0
    leaving = (
        max(0.0, 1.0 - (clip.duration_frames - offset) / window)
        if effects.exit_effect == "Pan"
        else 0.0
    )
    return max(-1.0, min(1.0, entering + leaving))


def qualified_still_drift(clip: Clip, timeline_frame: int) -> float | None:
    """Diagonal Drift position -1 (bottom-left), 0 (center), +1 (top-right).

    Drift shares the W4 quarter-second IN/OUT window with Pan. This value
    drives bounded simultaneous X and Y overscan crops, not visual opacity.
    """
    if clip.properties == ClipProperties():
        return None
    props = clip.properties
    effects = props.effects
    qualified = (
        clip.image_hold_frames is not None
        and props.transition.preset == "none"
        and effects.enter_effect in {"None", "Drift"}
        and effects.exit_effect in {"None", "Drift"}
        and (effects.enter_effect == "Drift" or effects.exit_effect == "Drift")
        and effects.intensity_percent == 100
        and replace(props, effects=EffectProperties()) == ClipProperties()
    )
    if not qualified:
        return None
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("drift frame outside clip")
    window = max(1.0, min(0.25 * clip.timeline_start.fps, clip.duration_frames / 2.0))
    entering = -max(0.0, 1.0 - offset / window) if effects.enter_effect == "Drift" else 0.0
    leaving = (
        max(0.0, 1.0 - (clip.duration_frames - offset) / window)
        if effects.exit_effect == "Drift"
        else 0.0
    )
    return max(-1.0, min(1.0, entering + leaving))


def qualified_still_rise(clip: Clip, timeline_frame: int) -> float | None:
    """Bounded vertical W4 Rise displacement: down on IN and OUT, centered midclip.

    W4's Rise uses an 8% positive Y overlay excursion, quarter-second
    timing, and full-intensity single-effect qualification. Source cropping
    must cover the canvas throughout rather than exposing empty borders.
    """
    if clip.properties == ClipProperties():
        return None
    props = clip.properties
    effects = props.effects
    qualified = (
        clip.image_hold_frames is not None
        and props.transition.preset == "none"
        and effects.enter_effect in {"None", "Rise"}
        and effects.exit_effect in {"None", "Rise"}
        and (effects.enter_effect == "Rise" or effects.exit_effect == "Rise")
        and effects.intensity_percent == 100
        and replace(props, effects=EffectProperties()) == ClipProperties()
    )
    if not qualified:
        return None
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("rise frame outside clip")
    window = max(1.0, min(0.25 * clip.timeline_start.fps, clip.duration_frames / 2.0))
    entering = max(0.0, 1.0 - offset / window) if effects.enter_effect == "Rise" else 0.0
    leaving = (
        max(0.0, 1.0 - (clip.duration_frames - offset) / window)
        if effects.exit_effect == "Rise"
        else 0.0
    )
    return max(0.0, min(1.0, entering + leaving))


def qualified_still_breathe(clip: Clip, timeline_frame: int) -> float | None:
    """W4 Breathe is bounded 0.98→1.00 on enter, 1.00→0.98 on exit.

    Only a single V1 still HOLD, default other properties and one Breathe
    preset are qualified; unsupported mixed presets must fail closed.
    """
    if clip.properties == ClipProperties():
        return None
    props = clip.properties
    effects = props.effects
    qualified = (
        clip.image_hold_frames is not None
        and props.transition.preset == "none"
        and effects.enter_effect in {"None", "Breathe"}
        and effects.exit_effect in {"None", "Breathe"}
        and (effects.enter_effect == "Breathe" or effects.exit_effect == "Breathe")
        and effects.intensity_percent == 100
        and replace(props, effects=EffectProperties()) == ClipProperties()
    )
    if not qualified:
        return None
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("breathe frame outside clip")
    window = max(1.0, min(0.25 * clip.timeline_start.fps, clip.duration_frames / 2.0))
    entering = max(0.0, 1.0 - offset / window) if effects.enter_effect == "Breathe" else 0.0
    leaving = (
        max(0.0, 1.0 - (clip.duration_frames - offset) / window)
        if effects.exit_effect == "Breathe"
        else 0.0
    )
    return 1.0 - 0.02 * max(0.0, min(1.0, entering + leaving))


def qualified_still_visibility(clip: Clip, timeline_frame: int) -> float | None:
    """Return 0..1 image visibility, None for unmodified clips; reject others."""
    if (
        clip.properties == ClipProperties()
        or qualified_still_pan(clip, timeline_frame) is not None
        or qualified_still_drift(clip, timeline_frame) is not None
        or qualified_still_rise(clip, timeline_frame) is not None
        or qualified_still_breathe(clip, timeline_frame) is not None
    ):
        return None
    if clip.image_hold_frames is None:
        raise ValueError("unsupported still-image effect or transition")
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("effect frame outside clip")

    props = clip.properties
    if (
        props.transition.preset == "fade_black"
        and replace(props, transition=TransitionProperties()) == ClipProperties()
    ):
        window = min(float(props.transition.duration_frames), max(1.0, clip.duration_frames / 2.0))
        return min(1.0, offset / window, (clip.duration_frames - offset) / window)

    effects = props.effects
    qualified = (
        props.transition.preset == "none"
        and effects.enter_effect in {"None", "Fade"}
        and effects.exit_effect in {"None", "Fade"}
        and (effects.enter_effect == "Fade" or effects.exit_effect == "Fade")
        and effects.intensity_percent == 100
        and replace(props, effects=EffectProperties()) == ClipProperties()
    )
    if not qualified:
        raise ValueError("unsupported still-image effect or transition")

    # W4: Fade uses a min(0.25 seconds, half clip duration) time window.
    window = min(0.25 * clip.timeline_start.fps, clip.duration_frames / 2.0)
    entering = offset / window if effects.enter_effect == "Fade" else 1.0
    leaving = (clip.duration_frames - offset) / window if effects.exit_effect == "Fade" else 1.0
    return max(0.0, min(1.0, entering, leaving))


def qualified_fade_black_visibility(clip: Clip, timeline_frame: int) -> float | None:
    """Compatibility alias for previous Pilot A frame-qualification API."""
    return qualified_still_visibility(clip, timeline_frame)
