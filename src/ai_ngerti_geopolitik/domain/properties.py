"""Canonical clip-property value objects for SF-STEP 11 W3."""

from __future__ import annotations

from dataclasses import dataclass


class PropertyValidationError(ValueError):
    pass


def _bounded(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise PropertyValidationError(
            f"{name} must be between {minimum} and {maximum}, got {value}"
        )


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
class ClipProperties:
    video: VideoProperties = VideoProperties()
    audio: AudioProperties = AudioProperties()
    color: ColorProperties = ColorProperties()
    speed: SpeedProperties = SpeedProperties()
