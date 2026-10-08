"""Bounded still-frame PNG sequence export from canonical image-only projects.

This is a read-only intermediate frame sequence for future engine parity tests,
not a native FFmpeg/MLT render or final MP4 export. Run off the Qt GUI thread.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.still_frame_preview import (
    StillFramePreviewError,
    render_still_frame,
)

_MAX_BATCH_FRAMES = 300
_MAX_BATCH_BYTES = 512 * 1024 * 1024


class StillSequenceExportError(RuntimeError):
    """Safe export failure without leaking media or destination paths."""


def export_still_frame_sequence(
    state: ProjectState,
    destination: Path,
    *,
    start_frame: int,
    count: int,
) -> Path:
    """Stage PNG frames + verified manifest, then publish a new directory.

    Frames use canonical absolute numbering, exact FPS and source timestamps.
    If decoding fails or input media changes, discard the staged directory.
    Existing output directories are never deliberately overwritten.
    """
    if (
        type(start_frame) is not int
        or type(count) is not int
        or start_frame < 0
        or not 1 <= count <= _MAX_BATCH_FRAMES
        or start_frame + count > state.timeline_end_frame
    ):
        raise StillSequenceExportError("frame sequence range is invalid or too large")

    if destination.suffix.lower() in {".png", ".mp4", ".zip"}:
        raise StillSequenceExportError("frame sequence output must be a new directory")
    if destination.exists() or destination.is_symlink():
        raise StillSequenceExportError("frame sequence destination already exists")

    staging: Path | None = None
    phase = "prepare"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise StillSequenceExportError("frame sequence destination already exists")
        staging = Path(tempfile.mkdtemp(prefix=".angseq-", dir=destination.parent))
        entries: list[dict[str, object]] = []
        total_bytes = 0
        for frame in range(start_frame, start_frame + count):
            phase = "render"
            image = render_still_frame(state, frame)
            filename = f"frame_{frame:06d}.png"
            target = staging / filename
            phase = "save-png"
            if not image.save(str(target)):
                raise StillSequenceExportError("a preview frame could not be written")
            phase = "hash-png"
            file_size = target.stat().st_size
            total_bytes += file_size
            if total_bytes > _MAX_BATCH_BYTES:
                raise StillSequenceExportError("frame sequence exceeds size limit")
            entries.append(
                {
                    "frame": frame,
                    "png": filename,
                    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                    "bytes": file_size,
                }
            )

        phase = "manifest"
        manifest = {
            "format": "ang-still-sequence-v1",
            "project_id": state.project_id,
            "project_semantic_sha256": state.semantic_hash(),
            "fps": state.fps,
            "start_frame": start_frame,
            "end_frame_exclusive": start_frame + count,
            "frame_count": count,
            "frames": entries,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if destination.exists() or destination.is_symlink():
            raise StillSequenceExportError("frame sequence destination already exists")
        phase = "publish"
        os.rename(staging, destination)
        staging = None
        return destination
    except StillSequenceExportError:
        raise
    except (StillFramePreviewError, OSError, RuntimeError, ValueError) as error:
        raise StillSequenceExportError(
            f"frame sequence could not be safely exported ({phase}: {type(error).__name__})"
        ) from None
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)


_MAX_PROJECT_FRAMES = 18_000
_MAX_PROJECT_PNG_BYTES = 8 * 1024 * 1024 * 1024


def export_complete_still_sequence(
    state: ProjectState,
    destination: Path,
    *,
    batch_size: int = _MAX_BATCH_FRAMES,
) -> Path:
    """Export the full image-only timeline in bounded batches, atomically.

    The outer manifest references each verified batch manifest. No FFmpeg,
    mixed-media composition, partial publish or silent frame truncation.
    """
    if (
        type(batch_size) is not int
        or not 1 <= batch_size <= _MAX_BATCH_FRAMES
        or not 1 <= state.timeline_end_frame <= _MAX_PROJECT_FRAMES
    ):
        raise StillSequenceExportError("full frame sequence limits are invalid")
    if destination.suffix.lower() in {".png", ".mp4", ".zip"}:
        raise StillSequenceExportError("frame sequence output must be a new directory")
    if destination.exists() or destination.is_symlink():
        raise StillSequenceExportError("frame sequence destination already exists")

    staging: Path | None = None
    phase = "prepare"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise StillSequenceExportError("frame sequence destination already exists")
        staging = Path(tempfile.mkdtemp(prefix=".angfull-", dir=destination.parent))
        batches: list[dict[str, object]] = []
        total_bytes = 0
        for start in range(0, state.timeline_end_frame, batch_size):
            count = min(batch_size, state.timeline_end_frame - start)
            folder = f"batch_{start:06d}_{start + count:06d}"
            phase = "render-batch"
            batch = export_still_frame_sequence(
                state, staging / folder, start_frame=start, count=count
            )
            phase = "verify-batch"
            manifest_bytes = (batch / "manifest.json").read_bytes()
            manifest = json.loads(manifest_bytes)
            if (
                manifest["start_frame"] != start
                or manifest["end_frame_exclusive"] != start + count
                or manifest["frame_count"] != count
                or manifest["project_semantic_sha256"] != state.semantic_hash()
            ):
                raise StillSequenceExportError("batch manifest is inconsistent")
            total_bytes += sum(int(entry["bytes"]) for entry in manifest["frames"])
            if total_bytes > _MAX_PROJECT_PNG_BYTES:
                raise StillSequenceExportError("full frame sequence exceeds size limit")
            batches.append(
                {
                    "directory": folder,
                    "start_frame": start,
                    "end_frame_exclusive": start + count,
                    "frame_count": count,
                    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                }
            )

        # A source file could change after an earlier batch was generated.
        # Recheck every scene boundary once more before publishing output.
        phase = "final-source-verification"
        starts = {clip.timeline_start.frames for track in state.tracks for clip in track.clips}
        for frame in sorted(starts):
            render_still_frame(state, frame)

        phase = "write-master-manifest"
        master = {
            "format": "ang-still-project-v1",
            "project_id": state.project_id,
            "project_semantic_sha256": state.semantic_hash(),
            "fps": state.fps,
            "start_frame": 0,
            "end_frame_exclusive": state.timeline_end_frame,
            "frame_count": state.timeline_end_frame,
            "batch_count": len(batches),
            "png_bytes": total_bytes,
            "batches": batches,
        }
        (staging / "manifest.json").write_text(
            json.dumps(master, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if destination.exists() or destination.is_symlink():
            raise StillSequenceExportError("frame sequence destination already exists")
        phase = "publish"
        os.rename(staging, destination)
        staging = None
        return destination
    except StillSequenceExportError:
        raise
    except (StillFramePreviewError, OSError, RuntimeError, ValueError, KeyError, TypeError) as err:
        raise StillSequenceExportError(
            f"full frame sequence could not be safely exported ({phase}: {type(err).__name__})"
        ) from None
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)
