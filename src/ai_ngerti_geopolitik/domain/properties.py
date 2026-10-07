"""Canonical clip-property value objects for SF-STEP 11 W3/W4."""

from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_W4_EFFECTS = (
    "None",
    "Fade",
    "Pop",
    "Breathe",
    "Stomp",
    "Tumble",
    "Tectonic",
    "Rise",
    "Pan",
    "Drift",
)
UNSUPPORTED_LEGACY_EFFECTS = (
    "Wipe",
    "Blur",
    "Succession",
    "Baseline",
    "Neon",
    "Scrapbook",
    "Brush",
    "Ink",
    "Digital",
    "Spray Paint",
    "Sketch",
    "Gradient",
)
SUPPORTED_W4_TRANSITIONS = ("none", "fade_black")
TITLE_POSITIONS = ("top", "center", "bottom")


class PropertyValidationError(ValueError):
    pass


def _bounded(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise PropertyValidationError(
            f"{name} must be between {minimum} and {maximum}, got {value}"
        )


def _hex_color(value: str) -> None:
    if len(value) != 6 or any(character not in "0123456789abcdefABCDEF" for character in value):
        raise PropertyValidationError("color_hex must contain exactly six hexadecimal digits")


@dataclass(frozen=True, slots=True)
class VideoProperties:
    position_x: int = 0
    position_y: int = 0
    scale_x_percent: int = 100
    scale_y_percent: int = 100
    rotation_tenths: int = 0
    opacity_percent: int = 100
    crop_left_percent: int = 0
    crop_top_percent: int = 0
    crop_right_percent: int = 0
    crop_bottom_percent: int = 0

    def __post_init__(self) -> None:
        _bounded("position_x", self.position_x, -10000, 10000)
        _bounded("position_y", self.position_y, -10000, 10000)
        _bounded("scale_x_percent", self.scale_x_percent, 10, 400)
        _bounded("scale_y_percent", self.scale_y_percent, 10, 400)
        _bounded("rotation_tenths", self.rotation_tenths, -3600, 3600)
        _bounded("opacity_percent", self.opacity_percent, 0, 100)
        for name, value in (
            ("crop_left_percent", self.crop_left_percent),
            ("crop_top_percent", self.crop_top_percent),
            ("crop_right_percent", self.crop_right_percent),
            ("crop_bottom_percent", self.crop_bottom_percent),
        ):
            _bounded(name, value, 0, 95)
        if self.crop_left_percent + self.crop_right_percent >= 100:
            raise PropertyValidationError("horizontal crop must leave visible pixels")
        if self.crop_top_percent + self.crop_bottom_percent >= 100:
            raise PropertyValidationError("vertical crop must leave visible pixels")


@dataclass(frozen=True, slots=True)
class AudioProperties:
    volume_percent: int = 100
    pan_percent: int = 0
    fade_in_frames: int = 0
    fade_out_frames: int = 0

    def __post_init__(self) -> None:
        _bounded("volume_percent", self.volume_percent, 0, 400)
        _bounded("pan_percent", self.pan_percent, -100, 100)
        _bounded("fade_in_frames", self.fade_in_frames, 0, 1_000_000)
        _bounded("fade_out_frames", self.fade_out_frames, 0, 1_000_000)


@dataclass(frozen=True, slots=True)
class ColorProperties:
    brightness_percent: int = 0
    exposure_tenths_ev: int = 0
    contrast_percent: int = 0
    saturation_percent: int = 0
    temperature_percent: int = 0
    tint_percent: int = 0

    def __post_init__(self) -> None:
        _bounded("brightness_percent", self.brightness_percent, -100, 100)
        _bounded("exposure_tenths_ev", self.exposure_tenths_ev, -50, 50)
        _bounded("contrast_percent", self.contrast_percent, -100, 100)
        _bounded("saturation_percent", self.saturation_percent, -100, 200)
        _bounded("temperature_percent", self.temperature_percent, -100, 100)
        _bounded("tint_percent", self.tint_percent, -100, 100)


@dataclass(frozen=True, slots=True)
class SpeedProperties:
    rate_percent: int = 100

    def __post_init__(self) -> None:
        _bounded("rate_percent", self.rate_percent, 25, 400)


@dataclass(frozen=True, slots=True)
class TitleProperties:
    enabled: bool = False
    text: str = ""
    font_size: int = 54
    position: str = "bottom"
    color_hex: str = "FFFFFF"
    background_opacity_percent: int = 55

    def __post_init__(self) -> None:
        if len(self.text) > 160:
            raise PropertyValidationError("title text must be at most 160 characters")
        if self.enabled and not self.text.strip():
            raise PropertyValidationError("enabled title requires non-empty text")
        _bounded("font_size", self.font_size, 12, 160)
        if self.position not in TITLE_POSITIONS:
            raise PropertyValidationError(f"unsupported title position: {self.position}")
        _hex_color(self.color_hex)
        _bounded(
            "background_opacity_percent",
            self.background_opacity_percent,
            0,
            100,
        )


@dataclass(frozen=True, slots=True)
class TransitionProperties:
    preset: str = "none"
    duration_frames: int = 0

    def __post_init__(self) -> None:
        if self.preset not in SUPPORTED_W4_TRANSITIONS:
            raise PropertyValidationError(f"unsupported transition preset: {self.preset}")
        if self.preset == "none":
            if self.duration_frames != 0:
                raise PropertyValidationError("none transition must use zero duration")
            return
        _bounded("duration_frames", self.duration_frames, 1, 300)


@dataclass(frozen=True, slots=True)
class EffectProperties:
    enter_effect: str = "None"
    exit_effect: str = "None"
    intensity_percent: int = 100
    locked: bool = False

    def __post_init__(self) -> None:
        if self.enter_effect not in SUPPORTED_W4_EFFECTS:
            raise PropertyValidationError(f"unsupported enter effect: {self.enter_effect}")
        if self.exit_effect not in SUPPORTED_W4_EFFECTS:
            raise PropertyValidationError(f"unsupported exit effect: {self.exit_effect}")
        _bounded("intensity_percent", self.intensity_percent, 0, 200)


@dataclass(frozen=True, slots=True)
class ClipProperties:
    video: VideoProperties = VideoProperties()
    audio: AudioProperties = AudioProperties()
    color: ColorProperties = ColorProperties()
    speed: SpeedProperties = SpeedProperties()
    title: TitleProperties = TitleProperties()
    transition: TransitionProperties = TransitionProperties()
    effects: EffectProperties = EffectProperties()
