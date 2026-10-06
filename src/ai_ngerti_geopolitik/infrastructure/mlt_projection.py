"""MLT timeline projection derived only from canonical ProjectState."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState


class MltProjectionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MltSegment:
    clip_id: str
    asset_id: str
    resource: str
    timeline_start_frame: int
    timeline_end_frame: int
    source_in_frame: int
    source_out_frame: int

    @property
    def duration_frames(self) -> int:
        return self.timeline_end_frame - self.timeline_start_frame


@dataclass(frozen=True, slots=True)
class MltTimelinePlan:
    project_revision: int
    fps: int
    segments: tuple[MltSegment, ...]

    @property
    def timeline_end_frame(self) -> int:
        return self.segments[-1].timeline_end_frame if self.segments else 0

    def melt_source_arguments(self, start_frame: int = 0) -> list[str]:
        if not self.segments:
            raise MltProjectionError("MLT timeline is empty")
        if start_frame < 0 or start_frame >= self.timeline_end_frame:
            raise MltProjectionError(f"start frame outside MLT timeline: {start_frame}")

        arguments: list[str] = []
        for segment in self.segments:
            if segment.timeline_end_frame <= start_frame:
                continue
            offset = max(0, start_frame - segment.timeline_start_frame)
            source_in = segment.source_in_frame + offset
            source_out_inclusive = segment.source_out_frame - 1
            if source_in > source_out_inclusive:
                continue
            arguments.extend(
                [
                    segment.resource,
                    f"in={source_in}",
                    f"out={source_out_inclusive}",
                ]
            )
            start_frame = segment.timeline_end_frame
        if not arguments:
            raise MltProjectionError("no MLT segments remain after seek")
        return arguments


def build_mlt_timeline_plan(state: ProjectState, track_id: str = "V1") -> MltTimelinePlan:
    state.validate()
    track = state.track(track_id)
    clips = sorted(track.clips, key=lambda clip: clip.timeline_start.frames)
    if not clips:
        raise MltProjectionError("MLT projection requires at least one clip")

    expected_start = 0
    segments: list[MltSegment] = []
    for clip in clips:
        if not clip.enabled:
            raise MltProjectionError("W2 MLT projection does not silently skip disabled clips")
        if clip.timeline_start.frames != expected_start:
            raise MltProjectionError("W2 MLT playback requires a contiguous V1 timeline")
        asset = state.asset(clip.asset_id)
        if asset.media_type != "video":
            raise MltProjectionError("MLT V1 playback requires video assets")
        if asset.availability != "online":
            raise MltProjectionError(
                f"MLT playback blocked by {asset.asset_id} availability={asset.availability}"
            )
        resource = str(Path(asset.path_ref))
        segments.append(
            MltSegment(
                clip_id=clip.clip_id,
                asset_id=clip.asset_id,
                resource=resource,
                timeline_start_frame=clip.timeline_start.frames,
                timeline_end_frame=clip.timeline_end_frame,
                source_in_frame=clip.source_in.frames,
                source_out_frame=clip.source_out.frames,
            )
        )
        expected_start = clip.timeline_end_frame
    return MltTimelinePlan(state.revision, state.fps, tuple(segments))
