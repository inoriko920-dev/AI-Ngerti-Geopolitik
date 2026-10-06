"""Pure STEP 10 project/timeline model.

All canonical edit time is stored as integer frames tied to an explicit FPS.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from fractions import Fraction


class DomainValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True, order=True)
class FrameTime:
    frames: int
    fps: int

    def __post_init__(self) -> None:
        if self.frames < 0:
            raise DomainValidationError("frames must be non-negative")
        if self.fps <= 0:
            raise DomainValidationError("fps must be positive")

    @property
    def seconds(self) -> Fraction:
        return Fraction(self.frames, self.fps)


@dataclass(frozen=True, slots=True)
class Asset:
    asset_id: str
    path_ref: str
    media_type: str
    duration: FrameTime
    width: int
    height: int
    has_audio: bool
    fingerprint_sha256: str

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise DomainValidationError("asset_id is required")
        if self.media_type != "video":
            raise DomainValidationError("STEP 10 slice accepts video assets only")
        if self.width <= 0 or self.height <= 0:
            raise DomainValidationError("video dimensions must be positive")
        if len(self.fingerprint_sha256) != 64:
            raise DomainValidationError("asset fingerprint must be SHA-256")


@dataclass(frozen=True, slots=True)
class Clip:
    clip_id: str
    asset_id: str
    timeline_start: FrameTime
    source_in: FrameTime
    source_out: FrameTime
    enabled: bool = True

    def __post_init__(self) -> None:
        fps_values = {self.timeline_start.fps, self.source_in.fps, self.source_out.fps}
        if len(fps_values) != 1:
            raise DomainValidationError("clip time values must share one FPS")
        if self.source_out.frames <= self.source_in.frames:
            raise DomainValidationError("clip source_out must be after source_in")

    @property
    def duration_frames(self) -> int:
        return self.source_out.frames - self.source_in.frames

    @property
    def timeline_end_frame(self) -> int:
        return self.timeline_start.frames + self.duration_frames


@dataclass(frozen=True, slots=True)
class Track:
    track_id: str
    kind: str
    order: int
    clips: tuple[Clip, ...] = ()

    def __post_init__(self) -> None:
        if self.kind != "video":
            raise DomainValidationError("STEP 10 slice uses a video track")
        if self.order < 0:
            raise DomainValidationError("track order must be non-negative")


@dataclass(frozen=True, slots=True)
class ProjectState:
    project_id: str
    name: str
    schema_version: int
    fps: int
    revision: int
    assets: tuple[Asset, ...] = ()
    tracks: tuple[Track, ...] = ()

    @classmethod
    def create(cls, project_id: str, name: str, fps: int = 30) -> "ProjectState":
        if not project_id or not name:
            raise DomainValidationError("project identity is required")
        if fps <= 0:
            raise DomainValidationError("fps must be positive")
        return cls(
            project_id=project_id,
            name=name,
            schema_version=1,
            fps=fps,
            revision=0,
        )

    def asset(self, asset_id: str) -> Asset:
        for asset in self.assets:
            if asset.asset_id == asset_id:
                return asset
        raise DomainValidationError(f"unknown asset: {asset_id}")

    def clip(self, clip_id: str) -> Clip:
        for track in self.tracks:
            for clip in track.clips:
                if clip.clip_id == clip_id:
                    return clip
        raise DomainValidationError(f"unknown clip: {clip_id}")

    def track(self, track_id: str) -> Track:
        for track in self.tracks:
            if track.track_id == track_id:
                return track
        raise DomainValidationError(f"unknown track: {track_id}")

    def validate(self) -> None:
        if self.schema_version != 1:
            raise DomainValidationError("unsupported schema version")
        if self.revision < 0:
            raise DomainValidationError("revision must be non-negative")
        asset_ids = [asset.asset_id for asset in self.assets]
        if len(asset_ids) != len(set(asset_ids)):
            raise DomainValidationError("duplicate asset id")
        clip_ids: list[str] = []
        for asset in self.assets:
            if asset.duration.fps != self.fps:
                raise DomainValidationError("asset FPS must match project FPS in STEP 10")
        for track in self.tracks:
            last_end = 0
            for clip in sorted(track.clips, key=lambda item: item.timeline_start.frames):
                if clip.timeline_start.fps != self.fps:
                    raise DomainValidationError("clip FPS must match project FPS")
                asset = self.asset(clip.asset_id)
                if clip.source_out.frames > asset.duration.frames:
                    raise DomainValidationError("clip exceeds asset duration")
                if clip.timeline_start.frames < last_end:
                    raise DomainValidationError("overlapping STEP 10 clips are not supported")
                last_end = clip.timeline_end_frame
                clip_ids.append(clip.clip_id)
        if len(clip_ids) != len(set(clip_ids)):
            raise DomainValidationError("duplicate clip id")

    def semantic_dict(self, *, include_revision: bool = False) -> dict[str, object]:
        data = asdict(self)
        if not include_revision:
            data.pop("revision", None)
        return data

    def semantic_json(self, *, include_revision: bool = False) -> str:
        return json.dumps(
            self.semantic_dict(include_revision=include_revision),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def semantic_hash(self) -> str:
        return hashlib.sha256(self.semantic_json().encode("utf-8")).hexdigest()

    def with_revision(self, revision: int) -> "ProjectState":
        return replace(self, revision=revision)
