"""FFmpeg qualification projection for canonical W3 clip properties.

This remains a MediaEnginePort qualification adapter. It does not change the
STEP 11 production-engine priority decision recorded for MLT.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import Clip


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def atempo_chain(rate_percent: int) -> tuple[float, ...]:
    factor = rate_percent / 100.0
    parts: list[float] = []
    while factor > 2.0 + 1e-9:
        parts.append(2.0)
        factor /= 2.0
    while factor < 0.5 - 1e-9:
        parts.append(0.5)
        factor /= 0.5
    if abs(factor - 1.0) > 1e-9 or not parts:
        parts.append(factor)
    return tuple(parts)


@dataclass(frozen=True, slots=True)
class W3FilterPlan:
    video_filters: tuple[str, ...]
    audio_filters: tuple[str, ...]
    overlay_x: str
    overlay_y: str
    duration_seconds: float


def build_w3_filter_plan(clip: Clip, fps: int) -> W3FilterPlan:
    if fps <= 0:
        raise ValueError("fps must be positive")
    properties = clip.properties
    video = properties.video
    color = properties.color
    audio = properties.audio
    speed = properties.speed

    crop_width = (100 - video.crop_left_percent - video.crop_right_percent) / 100.0
    crop_height = (100 - video.crop_top_percent - video.crop_bottom_percent) / 100.0
    crop_x = video.crop_left_percent / 100.0
    crop_y = video.crop_top_percent / 100.0
    scale_x = video.scale_x_percent / 100.0
    scale_y = video.scale_y_percent / 100.0
    rotation = video.rotation_tenths / 10.0
    opacity = video.opacity_percent / 100.0

    brightness = max(
        -1.0,
        min(
            1.0,
            color.brightness_percent / 100.0 + color.exposure_tenths_ev / 50.0,
        ),
    )
    contrast = max(0.0, 1.0 + color.contrast_percent / 100.0)
    saturation = max(0.0, 1.0 + color.saturation_percent / 100.0)
    temperature = color.temperature_percent / 200.0
    tint = color.tint_percent / 200.0

    video_filters = [
        (
            "crop="
            f"trunc(iw*{_number(crop_width)}/2)*2:"
            f"trunc(ih*{_number(crop_height)}/2)*2:"
            f"iw*{_number(crop_x)}:ih*{_number(crop_y)}"
        ),
        (
            "scale="
            f"max(2,trunc(iw*{_number(scale_x)}/2)*2):"
            f"max(2,trunc(ih*{_number(scale_y)}/2)*2)"
        ),
    ]
    if abs(rotation) > 1e-9:
        radians = rotation * 3.141592653589793 / 180.0
        video_filters.append(
            "rotate="
            f"{_number(radians)}:"
            "ow=rotw(iw):oh=roth(ih):c=black@0"
        )
        video_filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")
    video_filters.extend(
        [
            (
                "eq="
                f"brightness={_number(brightness)}:"
                f"contrast={_number(contrast)}:"
                f"saturation={_number(saturation)}"
            ),
            (
                "colorbalance="
                f"rs={_number(temperature)}:"
                f"bs={_number(-temperature)}:"
                f"gm={_number(tint)}"
            ),
            "format=rgba",
            f"colorchannelmixer=aa={_number(opacity)}",
        ]
    )

    audio_filters: list[str] = []
    for factor in atempo_chain(speed.rate_percent):
        if abs(factor - 1.0) > 1e-9:
            audio_filters.append(f"atempo={_number(factor)}")
    audio_filters.append(f"volume={_number(audio.volume_percent / 100.0)}")
    audio_filters.append("aformat=channel_layouts=stereo")
    pan = audio.pan_percent
    left = 1.0 if pan <= 0 else 1.0 - pan / 100.0
    right = 1.0 if pan >= 0 else 1.0 + pan / 100.0
    audio_filters.append(
        f"pan=stereo|c0=c0*{_number(left)}|c1=c1*{_number(right)}"
    )

    duration_seconds = clip.duration_frames / fps
    fade_in = min(audio.fade_in_frames, clip.duration_frames)
    fade_out = min(audio.fade_out_frames, clip.duration_frames)
    if fade_in:
        audio_filters.append(f"afade=t=in:st=0:d={_number(fade_in / fps)}")
    if fade_out:
        start = max(0.0, (clip.duration_frames - fade_out) / fps)
        audio_filters.append(
            f"afade=t=out:st={_number(start)}:d={_number(fade_out / fps)}"
        )

    return W3FilterPlan(
        video_filters=tuple(video_filters),
        audio_filters=tuple(audio_filters),
        overlay_x=f"(main_w-overlay_w)/2+{video.position_x}",
        overlay_y=f"(main_h-overlay_h)/2+{video.position_y}",
        duration_seconds=duration_seconds,
    )
