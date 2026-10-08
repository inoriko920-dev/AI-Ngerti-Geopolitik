"""Read-only frame-exact PNG handoff validation before any future MP4 encoder.

This is an integrity gate, not authorization to execute FFmpeg, create MP4,
enable GUI Export, or assume subtitle/audio/transition parity.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.still_frame_preview import render_still_frame

_MAX_FRAMES = 18_000
_MAX_PNG_BYTES = 8 * 1024 * 1024 * 1024
_MAX_BATCH_FRAMES = 300
_MAX_MASTER_BYTES = 2 * 1024 * 1024
_MAX_BATCH_MANIFEST_BYTES = 256 * 1024
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_SHA256 = re.compile(r"[a-f0-9]{64}")


class StillSequenceVerificationError(RuntimeError):
    """Path-free error for an untrusted or stale exported frame directory."""


@dataclass(frozen=True, slots=True)
class VerifiedStillSequence:
    """Immutable ordered inputs for a separately authorized encoder adapter."""

    project_semantic_sha256: str
    fps: int
    frame_count: int
    width: int
    height: int
    png_bytes: int
    frame_files: tuple[Path, ...]


def _load_json(path: Path, limit: int) -> tuple[dict[str, object], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("invalid manifest")
    if not 0 < path.stat().st_size <= limit:
        raise ValueError("manifest exceeds verification limits")
    contents = path.read_bytes()
    if not 0 < len(contents) <= limit:
        raise ValueError("manifest exceeds verification limits")
    decoded: object = json.loads(contents.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("manifest must be an object")
    return decoded, contents


def _integer(value: object, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("invalid numeric manifest value")
    return value


def _digest(value: object) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError("invalid manifest digest")
    return value


def _verify_png(path: Path, expected_hash: str, expected_bytes: int, size: tuple[int, int]) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or linked frame")
    before = path.stat()
    if before.st_size != expected_bytes:
        raise ValueError("frame size changed")
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        header = handle.read(24)
        if (
            len(header) != 24
            or header[:8] != _PNG_SIGNATURE
            or header[12:16] != b"IHDR"
            or int.from_bytes(header[8:12], "big") != 13
            or int.from_bytes(header[16:20], "big") != size[0]
            or int.from_bytes(header[20:24], "big") != size[1]
        ):
            raise ValueError("frame dimensions or header changed")
        sha.update(header)
        while chunk := handle.read(1024 * 1024):
            sha.update(chunk)
    after = path.stat()
    if (
        sha.hexdigest() != expected_hash
        or (before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    ):
        raise ValueError("frame checksum changed")


def _verify(state: ProjectState, root: Path) -> VerifiedStillSequence:
    state.validate()
    count = _integer(state.timeline_end_frame, 1, _MAX_FRAMES)
    project_sha = state.semantic_hash()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("frame source must be a real directory")
    master, _ = _load_json(root / "manifest.json", _MAX_MASTER_BYTES)
    if (
        master.get("format") != "ang-still-project-v1"
        or master.get("project_id") != state.project_id
        or master.get("project_semantic_sha256") != project_sha
        or type(master.get("fps")) is not int
        or master["fps"] != state.fps
        or type(master.get("start_frame")) is not int
        or master["start_frame"] != 0
        or type(master.get("end_frame_exclusive")) is not int
        or master["end_frame_exclusive"] != count
        or type(master.get("frame_count")) is not int
        or master["frame_count"] != count
    ):
        raise ValueError("master manifest disagrees with project")
    declared_bytes = _integer(master.get("png_bytes"), 1, _MAX_PNG_BYTES)
    batches = master.get("batches")
    if not isinstance(batches, list) or not 1 <= len(batches) <= count:
        raise ValueError("invalid master batch list")
    if _integer(master.get("batch_count"), 1, count) != len(batches):
        raise ValueError("invalid batch count")

    expected_root = {"manifest.json"}
    ordered: list[Path] = []
    cursor = 0
    total_bytes = 0
    dimensions = (state.settings.width, state.settings.height)
    for batch_record in batches:
        if not isinstance(batch_record, dict):
            raise ValueError("invalid batch record")
        batch_count = _integer(batch_record.get("frame_count"), 1, _MAX_BATCH_FRAMES)
        end = cursor + batch_count
        if end > count:
            raise ValueError("batch exceeds timeline")
        folder = f"batch_{cursor:06d}_{end:06d}"
        if (
            batch_record.get("directory") != folder
            or type(batch_record.get("start_frame")) is not int
            or batch_record["start_frame"] != cursor
            or type(batch_record.get("end_frame_exclusive")) is not int
            or batch_record["end_frame_exclusive"] != end
        ):
            raise ValueError("noncontiguous batch numbering")
        expected_root.add(folder)
        batch_dir = root / folder
        if batch_dir.is_symlink() or not batch_dir.is_dir():
            raise ValueError("invalid batch directory")
        batch, bytes_read = _load_json(batch_dir / "manifest.json", _MAX_BATCH_MANIFEST_BYTES)
        if hashlib.sha256(bytes_read).hexdigest() != _digest(
            batch_record.get("manifest_sha256")
        ):
            raise ValueError("batch manifest checksum changed")
        if (
            batch.get("format") != "ang-still-sequence-v1"
            or batch.get("project_id") != state.project_id
            or batch.get("project_semantic_sha256") != project_sha
            or type(batch.get("fps")) is not int
            or batch["fps"] != state.fps
            or type(batch.get("start_frame")) is not int
            or batch["start_frame"] != cursor
            or type(batch.get("end_frame_exclusive")) is not int
            or batch["end_frame_exclusive"] != end
            or type(batch.get("frame_count")) is not int
            or batch["frame_count"] != batch_count
        ):
            raise ValueError("batch manifest disagrees with project")
        entries = batch.get("frames")
        if not isinstance(entries, list) or len(entries) != batch_count:
            raise ValueError("missing frame rows")
        expected_batch = {"manifest.json"}
        for offset, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError("invalid frame record")
            frame = cursor + offset
            filename = f"frame_{frame:06d}.png"
            if (
                type(entry.get("frame")) is not int
                or entry["frame"] != frame
                or entry.get("png") != filename
            ):
                raise ValueError("frame sequence has a gap or wrong filename")
            expected_batch.add(filename)
            frame_bytes = _integer(entry.get("bytes"), 1, _MAX_PNG_BYTES)
            total_bytes += frame_bytes
            if total_bytes > _MAX_PNG_BYTES:
                raise ValueError("frame bytes exceed limits")
            path = batch_dir / filename
            _verify_png(path, _digest(entry.get("sha256")), frame_bytes, dimensions)
            ordered.append(path)
        if {p.name for p in batch_dir.iterdir()} != expected_batch:
            raise ValueError("unexpected batch contents")
        cursor = end

    if cursor != count or len(ordered) != count or total_bytes != declared_bytes:
        raise ValueError("master sequence length or bytes mismatch")
    if {p.name for p in root.iterdir()} != expected_root:
        raise ValueError("unexpected sequence contents")

    # Confirm original source images have not changed since the frame export.
    # This is a CPU/Qt still renderer, not an external multimedia process.
    boundaries = {clip.timeline_start.frames for track in state.tracks for clip in track.clips}
    for frame in sorted(boundaries):
        render_still_frame(state, frame)

    return VerifiedStillSequence(
        project_semantic_sha256=project_sha,
        fps=state.fps,
        frame_count=count,
        width=dimensions[0],
        height=dimensions[1],
        png_bytes=total_bytes,
        frame_files=tuple(ordered),
    )


def verify_complete_still_sequence(state: ProjectState, root: Path) -> VerifiedStillSequence:
    """Verify source, manifests and each PNG; perform no mutation or process launch."""
    try:
        return _verify(state, root)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, UnicodeError):
        raise StillSequenceVerificationError(
            "frame sequence did not pass integrity verification"
        ) from None
