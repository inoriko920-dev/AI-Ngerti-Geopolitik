"""Frame-exact qualification for the first still-image transition preset.

W4's native fade-through-black uses an inbound and outbound window,
each clamped to half a clip's duration. No overlapping clip/crossfade.
"""

from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.domain.project import Clip
from ai_ngerti_geopolitik.domain.properties import ClipProperties, TransitionProperties


def qualified_fade_black_visibility(clip: Clip, timeline_frame: int) -> float | None:
    """Return 0..1 visibility for a V1 HOLD fade or None for static clips."""
    if clip.properties == ClipProperties():
        return None
    transition = clip.properties.transition
    without_transition = replace(clip.properties, transition=TransitionProperties())
    if (
        clip.image_hold_frames is None
        or transition.preset != "fade_black"
        or without_transition != ClipProperties()
    ):
        raise ValueError("unsupported still-image effect or transition")
    offset = timeline_frame - clip.timeline_start.frames
    if not 0 <= offset < clip.duration_frames:
        raise ValueError("fade frame outside clip")
    window = min(float(transition.duration_frames), max(1.0, clip.duration_frames / 2.0))
    return min(1.0, offset / window, (clip.duration_frames - offset) / window)
