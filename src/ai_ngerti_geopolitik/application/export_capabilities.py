"""Fail-closed export capability projection for SF12-T01."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExportToolchain:
    ffmpeg_found: bool = False
    ffprobe_found: bool = False
    h264_encoder_found: bool = False
    h265_encoder_found: bool = False
    aac_encoder_found: bool = False

    @property
    def baseline_detected(self) -> bool:
        return (
            self.ffmpeg_found
            and self.ffprobe_found
            and self.h264_encoder_found
            and self.aac_encoder_found
        )


@dataclass(frozen=True, slots=True)
class ExportCapabilities:
    """Encoder existence alone cannot enable unqualified render controls."""

    toolchain: ExportToolchain = ExportToolchain()
    h264_export_qualified: bool = False
    render_handler_wired: bool = False

    @property
    def can_start_render(self) -> bool:
        return (
            self.toolchain.baseline_detected
            and self.h264_export_qualified
            and self.render_handler_wired
        )
