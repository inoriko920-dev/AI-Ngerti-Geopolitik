"""T06 explicit Windows qualification candidates; NOT a product capability claim.

Each accepted output profile must be backed by independently inspected real MP4
evidence. Presence in this list does not grant UI permissions or prove packaging.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ai_ngerti_geopolitik.application.export_request import ExportCodec, ExportRequest


class MatrixCell(StrEnum):
    H264_1440P30 = "h264_1440p30"
    H264_4K30 = "h264_4k30"
    H264_1080P60 = "h264_1080p60"
    H265_1080P30 = "h265_1080p30"


@dataclass(frozen=True, slots=True)
class MatrixProfile:
    cell: MatrixCell
    codec: ExportCodec
    width: int
    height: int
    fps: int
    encoder: str
    expected_decoder: str

    def matches(self, request: ExportRequest) -> bool:
        return request.codec is self.codec and (request.width, request.height, request.fps) == (
            self.width,
            self.height,
            self.fps,
        )


T06_CANDIDATE_PROFILES: tuple[MatrixProfile, ...] = (
    MatrixProfile(MatrixCell.H264_1440P30, ExportCodec.H264, 2560, 1440, 30, "libx264", "h264"),
    MatrixProfile(MatrixCell.H264_4K30, ExportCodec.H264, 3840, 2160, 30, "libx264", "h264"),
    MatrixProfile(MatrixCell.H264_1080P60, ExportCodec.H264, 1920, 1080, 60, "libx264", "h264"),
    MatrixProfile(MatrixCell.H265_1080P30, ExportCodec.H265, 1920, 1080, 30, "libx265", "hevc"),
)


def candidate_for_request(request: ExportRequest) -> MatrixProfile | None:
    return next((profile for profile in T06_CANDIDATE_PROFILES if profile.matches(request)), None)
