"""Pure canonical project/timeline model.

All canonical edit time is stored as integer frames tied to an explicit project FPS.
STEP 11 W5 extends schema-v1 compatibly with canonical subtitle/narration state while
preserving the W1-W4 media/project guarantees and stable identifiers.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from fractions import Fraction

from ai_ngerti_geopolitik.domain.properties import ClipProperties


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
class ProjectSettings:
    width: int = 1920
    height: int = 1080
    aspect_ratio: str = "16:9"

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise DomainValidationError("project resolution must be positive")
        if not self.aspect_ratio.strip():
            raise DomainValidationError("project aspect_ratio is required")


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
    source_name: str = ""
    file_size: int = 0
    sample_rate: int = 0
    availability: str = "online"

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise DomainValidationError("asset_id is required")
        if not self.path_ref:
            raise DomainValidationError("asset path_ref is required")
        if self.media_type not in {"video", "audio", "image"}:
            raise DomainValidationError(f"unsupported media_type: {self.media_type}")
        if self.duration.frames <= 0:
            raise DomainValidationError("asset duration must be positive")
        if self.media_type in {"video", "image"} and (self.width <= 0 or self.height <= 0):
            raise DomainValidationError("visual media dimensions must be positive")
        if self.media_type == "audio" and (self.width != 0 or self.height != 0):
            raise DomainValidationError("audio dimensions must be zero")
        if self.media_type == "audio" and not self.has_audio:
            raise DomainValidationError("audio asset must report has_audio")
        if len(self.fingerprint_sha256) != 64:
            raise DomainValidationError("asset fingerprint must be SHA-256")
        if self.file_size < 0:
            raise DomainValidationError("asset file_size must be non-negative")
        if self.sample_rate < 0:
            raise DomainValidationError("asset sample_rate must be non-negative")
        if self.availability not in {"online", "offline", "missing"}:
            raise DomainValidationError(f"invalid media availability: {self.availability}")


@dataclass(frozen=True, slots=True)
class Clip:
    clip_id: str
    asset_id: str
    timeline_start: FrameTime
    source_in: FrameTime
    source_out: FrameTime
    enabled: bool = True
    properties: ClipProperties = ClipProperties()

    def __post_init__(self) -> None:
        if not self.clip_id:
            raise DomainValidationError("clip_id is required")
        if not self.asset_id:
            raise DomainValidationError("clip asset_id is required")
        fps_values = {self.timeline_start.fps, self.source_in.fps, self.source_out.fps}
        if len(fps_values) != 1:
            raise DomainValidationError("clip time values must share one FPS")
        if self.source_out.frames <= self.source_in.frames:
            raise DomainValidationError("clip source_out must be after source_in")

    @property
    def source_duration_frames(self) -> int:
        return self.source_out.frames - self.source_in.frames

    @property
    def duration_frames(self) -> int:
        rate = self.properties.speed.rate_percent
        return max(1, (self.source_duration_frames * 100 + rate - 1) // rate)

    def timeline_frames_to_source_frames(self, timeline_frames: int) -> int:
        if timeline_frames <= 0:
            raise DomainValidationError("timeline frame duration must be positive")
        rate = self.properties.speed.rate_percent
        return max(1, (timeline_frames * rate + 50) // 100)

    def source_frame_at_timeline_offset(self, timeline_offset: int) -> int:
        if timeline_offset < 0 or timeline_offset >= self.duration_frames:
            raise DomainValidationError("timeline offset outside clip")
        source_offset = (timeline_offset * self.properties.speed.rate_percent) // 100
        return min(self.source_out.frames - 1, self.source_in.frames + source_offset)

    @property
    def timeline_end_frame(self) -> int:
        return self.timeline_start.frames + self.duration_frames


@dataclass(frozen=True, slots=True)
class Track:
    track_id: str
    kind: str
    order: int
    clips: tuple[Clip, ...] = ()
    name: str = ""
    locked: bool = False
    muted: bool = False
    visible: bool = True

    def __post_init__(self) -> None:
        if not self.track_id:
            raise DomainValidationError("track_id is required")
        if self.kind != "video":
            raise DomainValidationError("current canonical timeline supports video tracks")
        if self.order < 0:
            raise DomainValidationError("track order must be non-negative")
        if self.name and not self.name.strip():
            raise DomainValidationError("track name cannot be whitespace")


@dataclass(frozen=True, slots=True)
class Marker:
    marker_id: str
    frame: FrameTime
    label: str
    marker_type: str = "marker"

    def __post_init__(self) -> None:
        if not self.marker_id:
            raise DomainValidationError("marker_id is required")
        if not self.label.strip():
            raise DomainValidationError("marker label is required")
        if self.marker_type not in {"marker", "chapter", "note"}:
            raise DomainValidationError(f"unsupported marker_type: {self.marker_type}")




def _validate_hex_color(name: str, value: str) -> None:
    raw = value.strip()
    if len(raw) != 7 or not raw.startswith("#"):
        raise DomainValidationError(f"{name} must use #RRGGBB")
    if any(character not in "0123456789abcdefABCDEF" for character in raw[1:]):
        raise DomainValidationError(f"{name} must use #RRGGBB")


@dataclass(frozen=True, slots=True)
class WordTiming:
    word_id: str
    word: str
    start: FrameTime
    end: FrameTime

    def __post_init__(self) -> None:
        if not self.word_id:
            raise DomainValidationError("word timing id is required")
        if not self.word.strip():
            raise DomainValidationError("word timing text is required")
        if self.start.fps != self.end.fps:
            raise DomainValidationError("word timing values must share one FPS")
        if self.end.frames <= self.start.frames:
            raise DomainValidationError("word timing end must be after start")


@dataclass(frozen=True, slots=True)
class SubtitleStyle:
    font_family: str = "Arial"
    font_size: int = 54
    fill_color: str = "#FFFFFF"
    outline_color: str = "#111111"
    outline_width_tenths: int = 30
    shadow_tenths: int = 10
    background_box: bool = False
    background_opacity_percent: int = 0
    alignment: str = "bottom_center"
    margin_v: int = 64

    def __post_init__(self) -> None:
        if not self.font_family.strip():
            raise DomainValidationError("subtitle font family is required")
        if not 12 <= self.font_size <= 160:
            raise DomainValidationError("subtitle font size must be between 12 and 160")
        _validate_hex_color("subtitle fill color", self.fill_color)
        _validate_hex_color("subtitle outline color", self.outline_color)
        if not 0 <= self.outline_width_tenths <= 100:
            raise DomainValidationError("subtitle outline width must be between 0 and 10")
        if not 0 <= self.shadow_tenths <= 100:
            raise DomainValidationError("subtitle shadow must be between 0 and 10")
        if not 0 <= self.background_opacity_percent <= 100:
            raise DomainValidationError("subtitle background opacity must be between 0 and 100")
        if self.alignment not in {"top_center", "center", "bottom_center"}:
            raise DomainValidationError(f"unsupported subtitle alignment: {self.alignment}")
        if not 0 <= self.margin_v <= 1000:
            raise DomainValidationError("subtitle vertical margin must be between 0 and 1000")


@dataclass(frozen=True, slots=True)
class SubtitleAnimation:
    preset: str = "none"
    enter_frames: int = 0
    exit_frames: int = 0
    intensity_percent: int = 100
    highlight_color: str = "#FFD400"

    def __post_init__(self) -> None:
        if self.preset != "none":
            raise DomainValidationError(
                "subtitle animation is not render-qualified until S11-W5-005"
            )
        if self.enter_frames != 0 or self.exit_frames != 0:
            raise DomainValidationError("none subtitle animation must use zero timing")
        if not 0 <= self.intensity_percent <= 200:
            raise DomainValidationError("subtitle animation intensity must be between 0 and 200")
        _validate_hex_color("subtitle highlight color", self.highlight_color)


@dataclass(frozen=True, slots=True)
class SubtitleCue:
    cue_id: str
    index: int
    start: FrameTime
    end: FrameTime
    text: str
    word_timings: tuple[WordTiming, ...] = ()

    def __post_init__(self) -> None:
        if not self.cue_id:
            raise DomainValidationError("subtitle cue id is required")
        if self.index <= 0:
            raise DomainValidationError("subtitle cue index must be positive")
        if self.start.fps != self.end.fps:
            raise DomainValidationError("subtitle cue time values must share one FPS")
        if self.end.frames <= self.start.frames:
            raise DomainValidationError("subtitle cue end must be after start")
        if not self.text.strip():
            raise DomainValidationError("subtitle cue text is required")
        word_ids = [item.word_id for item in self.word_timings]
        if len(word_ids) != len(set(word_ids)):
            raise DomainValidationError("duplicate subtitle word timing id")
        previous_end = self.start.frames
        for timing in self.word_timings:
            if timing.start.fps != self.start.fps or timing.end.fps != self.start.fps:
                raise DomainValidationError("subtitle word timing FPS must match cue FPS")
            if timing.start.frames < self.start.frames or timing.end.frames > self.end.frames:
                raise DomainValidationError("subtitle word timing must stay inside cue")
            if timing.start.frames < previous_end:
                raise DomainValidationError("overlapping subtitle word timings are not supported")
            previous_end = timing.end.frames


@dataclass(frozen=True, slots=True)
class SubtitleTrack:
    source_ref: str
    cues: tuple[SubtitleCue, ...]
    style: SubtitleStyle = SubtitleStyle()
    animation: SubtitleAnimation = SubtitleAnimation()
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.source_ref.strip():
            raise DomainValidationError("subtitle source reference is required")
        if not self.cues:
            raise DomainValidationError("subtitle track requires at least one cue")
        cue_ids = [cue.cue_id for cue in self.cues]
        indexes = [cue.index for cue in self.cues]
        if len(cue_ids) != len(set(cue_ids)):
            raise DomainValidationError("duplicate subtitle cue id")
        if len(indexes) != len(set(indexes)):
            raise DomainValidationError("duplicate subtitle cue index")
        previous_end = 0
        previous_start = -1
        for cue in self.cues:
            if cue.start.frames < previous_start:
                raise DomainValidationError("subtitle cues must be ordered by start frame")
            if cue.start.frames < previous_end:
                raise DomainValidationError("overlapping subtitle cues are not canonical")
            previous_start = cue.start.frames
            previous_end = cue.end.frames


@dataclass(frozen=True, slots=True)
class NarrationTrack:
    narration_id: str
    asset_id: str
    timeline_start: FrameTime
    gain_percent: int = 100
    muted: bool = False
    fade_in_frames: int = 0
    fade_out_frames: int = 0

    def __post_init__(self) -> None:
        if not self.narration_id:
            raise DomainValidationError("narration id is required")
        if not self.asset_id:
            raise DomainValidationError("narration asset id is required")
        if not 0 <= self.gain_percent <= 400:
            raise DomainValidationError("narration gain must be between 0 and 400")
        if self.fade_in_frames < 0 or self.fade_out_frames < 0:
            raise DomainValidationError("narration fade frames must be non-negative")


@dataclass(frozen=True, slots=True)
class ProjectState:
    project_id: str
    name: str
    schema_version: int
    fps: int
    revision: int
    assets: tuple[Asset, ...] = ()
    tracks: tuple[Track, ...] = ()
    markers: tuple[Marker, ...] = ()
    subtitle: SubtitleTrack | None = None
    narration: NarrationTrack | None = None
    settings: ProjectSettings = ProjectSettings()

    @classmethod
    def create(
        cls,
        project_id: str,
        name: str,
        fps: int = 30,
        *,
        width: int = 1920,
        height: int = 1080,
        aspect_ratio: str = "16:9",
    ) -> ProjectState:
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
            settings=ProjectSettings(width, height, aspect_ratio),
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

    def marker(self, marker_id: str) -> Marker:
        for marker in self.markers:
            if marker.marker_id == marker_id:
                return marker
        raise DomainValidationError(f"unknown marker: {marker_id}")

    @property
    def timeline_end_frame(self) -> int:
        return max(
            (
                clip.timeline_end_frame
                for track in self.tracks
                for clip in track.clips
                if clip.enabled
            ),
            default=0,
        )

    def validate(self) -> None:
        if self.schema_version != 1:
            raise DomainValidationError("unsupported schema version")
        if self.fps <= 0:
            raise DomainValidationError("project FPS must be positive")
        if self.revision < 0:
            raise DomainValidationError("revision must be non-negative")
        self.settings.__post_init__()
        asset_ids = [asset.asset_id for asset in self.assets]
        if len(asset_ids) != len(set(asset_ids)):
            raise DomainValidationError("duplicate asset id")
        track_ids = [track.track_id for track in self.tracks]
        if len(track_ids) != len(set(track_ids)):
            raise DomainValidationError("duplicate track id")
        track_orders = [track.order for track in self.tracks]
        if len(track_orders) != len(set(track_orders)):
            raise DomainValidationError("duplicate track order")
        clip_ids: list[str] = []
        for asset in self.assets:
            if asset.duration.fps != self.fps:
                raise DomainValidationError("asset FPS must match project FPS")
        for track in self.tracks:
            last_end = 0
            for clip in sorted(track.clips, key=lambda item: item.timeline_start.frames):
                if clip.timeline_start.fps != self.fps:
                    raise DomainValidationError("clip FPS must match project FPS")
                asset = self.asset(clip.asset_id)
                if asset.media_type != "video":
                    raise DomainValidationError("video timeline clips must reference video assets")
                if clip.source_out.frames > asset.duration.frames:
                    raise DomainValidationError("clip exceeds asset duration")
                if clip.timeline_start.frames < last_end:
                    raise DomainValidationError("overlapping canonical clips are not supported")
                last_end = clip.timeline_end_frame
                clip_ids.append(clip.clip_id)
        if len(clip_ids) != len(set(clip_ids)):
            raise DomainValidationError("duplicate clip id")

        marker_ids = [marker.marker_id for marker in self.markers]
        if len(marker_ids) != len(set(marker_ids)):
            raise DomainValidationError("duplicate marker id")
        timeline_end = self.timeline_end_frame
        for marker in self.markers:
            if marker.frame.fps != self.fps:
                raise DomainValidationError("marker FPS must match project FPS")
            if timeline_end <= 0:
                raise DomainValidationError("markers require a non-empty timeline")
            if marker.frame.frames >= timeline_end:
                raise DomainValidationError("marker must be inside the timeline")

        if self.subtitle is not None:
            if timeline_end <= 0:
                raise DomainValidationError("subtitles require a non-empty timeline")
            for cue in self.subtitle.cues:
                if cue.start.fps != self.fps or cue.end.fps != self.fps:
                    raise DomainValidationError("subtitle cue FPS must match project FPS")
                if cue.end.frames > timeline_end:
                    raise DomainValidationError("subtitle cue must stay inside the timeline")

        if self.narration is not None:
            narration = self.narration
            if timeline_end <= 0:
                raise DomainValidationError("narration requires a non-empty timeline")
            if narration.timeline_start.fps != self.fps:
                raise DomainValidationError("narration FPS must match project FPS")
            if narration.timeline_start.frames >= timeline_end:
                raise DomainValidationError("narration must start inside the timeline")
            try:
                narration_asset = self.asset(narration.asset_id)
            except DomainValidationError as exc:
                raise DomainValidationError("narration must reference a canonical asset") from exc
            if narration_asset.media_type != "audio":
                raise DomainValidationError("narration must reference an audio asset")
            if narration.fade_in_frames > narration_asset.duration.frames:
                raise DomainValidationError("narration fade-in exceeds source duration")
            if narration.fade_out_frames > narration_asset.duration.frames:
                raise DomainValidationError("narration fade-out exceeds source duration")
            if narration.fade_in_frames + narration.fade_out_frames > narration_asset.duration.frames:
                raise DomainValidationError("narration fades exceed source duration")

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

    def with_revision(self, revision: int) -> ProjectState:
        return replace(self, revision=revision)
