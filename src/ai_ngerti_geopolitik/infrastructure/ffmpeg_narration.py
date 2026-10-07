"""Render-qualified W5-006 narration audio projection for FFmpeg."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import ProjectState


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def _milliseconds(frames: int, fps: int) -> int:
    return (frames * 1000 + fps // 2) // fps


@dataclass(frozen=True, slots=True)
class NarrationRenderPlan:
    source_path: str
    filters: tuple[str, ...]
    audible_frames: int


def build_narration_render_plan(state: ProjectState) -> NarrationRenderPlan | None:
    narration = state.narration
    if narration is None:
        return None
    asset = state.asset(narration.asset_id)
    audible_frames = min(
        asset.duration.frames,
        state.timeline_end_frame - narration.timeline_start.frames,
    )
    duration_seconds = audible_frames / state.fps
    gain = 0.0 if narration.muted else narration.gain_percent / 100.0

    filters = [
        f"atrim=start=0:end={_number(duration_seconds)}",
        "asetpts=PTS-STARTPTS",
        f"volume={_number(gain)}",
    ]
    if narration.fade_in_frames:
        filters.append("afade=t=in:st=0:d=" + _number(narration.fade_in_frames / state.fps))
    if narration.fade_out_frames:
        fade_duration = narration.fade_out_frames / state.fps
        fade_start = (audible_frames - narration.fade_out_frames) / state.fps
        filters.append(f"afade=t=out:st={_number(fade_start)}:d={_number(fade_duration)}")
    delay_ms = _milliseconds(narration.timeline_start.frames, state.fps)
    if delay_ms:
        filters.append(f"adelay={delay_ms}:all=1")
    return NarrationRenderPlan(
        source_path=asset.path_ref,
        filters=tuple(filters),
        audible_frames=audible_frames,
    )
