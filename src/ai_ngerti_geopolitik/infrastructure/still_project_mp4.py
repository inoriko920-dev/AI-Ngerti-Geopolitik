"""Pilot A: export a saved canonical still-image project as verified H.264 MP4.

This worker-only path takes the existing project model, exports complete
PNG batches, verifies them, then uses the owner-approved FFmpeg Pilot A.
It is NOT a general-purpose application render/export engine.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.pilot_a_still_mp4 import (
    PilotAError,
    PilotAResult,
    export_silent_h264_pilot_a,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import (
    StillSequenceExportError,
    export_complete_still_sequence,
)
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import (
    SilentH264PlanError,
    plan_silent_h264_mp4,
)


class StillProjectMP4Error(RuntimeError):
    """No source or output path is revealed in project MP4 export errors."""


def export_still_project_mp4(
    state: ProjectState,
    destination: Path,
    *,
    ffmpeg_path: Path,
    ffmpeg_sha256: str,
    ffprobe_path: Path,
    ffprobe_sha256: str,
    batch_size: int = 300,
    timeout_seconds: float = 60,
    should_cancel: Callable[[], bool] | None = None,
) -> PilotAResult:
    """Run the whole image-only project in a worker; never overwrite output.

    Temporary PNG frames are removed on success, timeout, cancellation or
    encode failure. A complete, probed MP4 is published only by Pilot A.
    Only the limited silent still-image codec is supported by this path.
    """
    try:
        if os.environ.get("ANG_PILOT_A_FFMPEG") != "1":
            raise ValueError("owner-gated Pilot A export is not enabled")
        if type(batch_size) is not int or not 1 <= batch_size <= 300:
            raise ValueError("batch size is outside verified limits")
        state.validate()
        if (
            not destination.is_absolute()
            or destination.suffix.lower() != ".mp4"
            or destination.exists()
            or destination.is_symlink()
            or not destination.parent.is_dir()
        ):
            raise ValueError("output is not a new MP4 in an existing directory")
        if should_cancel is not None and should_cancel():
            raise ValueError("project export cancelled before staging")
        with tempfile.TemporaryDirectory(prefix=".ang-still-mp4-", dir=destination.parent) as temp:
            frames = Path(temp) / "frames"
            export_complete_still_sequence(state, frames, batch_size=batch_size)
            if should_cancel is not None and should_cancel():
                raise ValueError("project export cancelled before encoder")
            plan = plan_silent_h264_mp4(state, frames, destination)
            result = export_silent_h264_pilot_a(
                plan,
                ffmpeg_path=ffmpeg_path,
                ffmpeg_sha256=ffmpeg_sha256,
                ffprobe_path=ffprobe_path,
                ffprobe_sha256=ffprobe_sha256,
                timeout_seconds=timeout_seconds,
                should_cancel=should_cancel,
            )
        return result
    except (
        OSError,
        RuntimeError,
        ValueError,
        TypeError,
        OverflowError,
    ):
        raise StillProjectMP4Error(
            "proyek gambar tidak dapat diekspor sebagai MP4 H.264 Pilot A"
        ) from None
