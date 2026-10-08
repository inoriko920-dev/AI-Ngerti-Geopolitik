"""SF12-T07 explicit subtitle/sharpen/quality candidates, no UI authorization.

Only specific FULL H264 1080p30 + AAC combinations can use this
experimental FFmpeg qualification path. No preset grants render permission.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.application.export_request import (
    ExportAudio,
    ExportCodec,
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
)


@dataclass(frozen=True, slots=True)
class StyleQualification:
    quality: ExportQuality
    sharpen: ExportSharpen
    subtitles: ExportSubtitles
    preset: str
    crf: int
    video_filter: str


T07_STYLE_CANDIDATES: tuple[StyleQualification, ...] = (
    StyleQualification(
        ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN, "ultrafast", 28, "null"
    ),
    StyleQualification(
        ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.OFF, "ultrafast", 28, "null"
    ),
    StyleQualification(
        ExportQuality.YOUTUBE_CLEAN, ExportSharpen.NONE, ExportSubtitles.BURN_IN,
        "medium", 21, "null"
    ),
    StyleQualification(
        ExportQuality.DOCUMENTARY_CRISP, ExportSharpen.NONE, ExportSubtitles.BURN_IN,
        "slow", 18, "null"
    ),
    StyleQualification(
        ExportQuality.HIGH, ExportSharpen.LIGHT, ExportSubtitles.BURN_IN,
        "ultrafast", 28, "unsharp=5:5:0.6:3:3:0.0"
    ),
    StyleQualification(
        ExportQuality.HIGH, ExportSharpen.CRISP, ExportSubtitles.BURN_IN,
        "ultrafast", 28, "unsharp=5:5:1.2:3:3:0.0"
    ),
)


def style_for_request(request: ExportRequest) -> StyleQualification | None:
    if (
        request.scope is not ExportScope.FULL
        or request.codec is not ExportCodec.H264
        or (request.width, request.height, request.fps) != (1920, 1080, 30)
        or request.audio is not ExportAudio.AAC
    ):
        return None
    return next(
        (
            item
            for item in T07_STYLE_CANDIDATES
            if (item.quality, item.sharpen, item.subtitles)
            == (request.quality, request.sharpen, request.subtitles)
        ),
        None,
    )
