"""CPU/Qt still-frame preview for canonical image clips (worker-only).

This adapter produces a real QImage for static SINGLE or DOUBLE image holds.
It does not implement MLT playback, transitions, animated effects or MP4 export.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRect, QSize, Qt
from PySide6.QtGui import QImage, QImageReader, QPainter

from ai_ngerti_geopolitik.domain import Asset, Clip, ProjectState
from ai_ngerti_geopolitik.domain.properties import ClipProperties

_MAX_SOURCE_BYTES = 128 * 1024 * 1024
_MAX_IMAGE_PIXELS = 100_000_000
_MAX_PREVIEW_PIXELS = 16_000_000
_MAX_SCALED_PIXELS = 16_000_000
_SUPPORTED = frozenset({".png", ".jpg", ".jpeg", ".webp"})


class StillFramePreviewError(RuntimeError):
    """User-safe preview rejection; private input media paths are never exposed."""


def _cover_size(width: int, height: int, source_width: int, source_height: int) -> QSize:
    if width * source_height >= height * source_width:
        w = width
        h = (source_height * width + source_width - 1) // source_width
    else:
        h = height
        w = (source_width * height + source_height - 1) // source_height
    if w <= 0 or h <= 0 or w * h > _MAX_SCALED_PIXELS:
        raise StillFramePreviewError("image proportions exceed preview limits")
    return QSize(w, h)


def _decode_verified(asset: Asset, size: QSize) -> QImage:
    path = Path(asset.path_ref)
    if (
        asset.media_type != "image"
        or asset.availability != "online"
        or path.suffix.lower() not in _SUPPORTED
        or path.is_symlink()
    ):
        raise StillFramePreviewError("image is not available for preview")
    try:
        before = path.stat()
        if not 0 < before.st_size <= _MAX_SOURCE_BYTES:
            raise StillFramePreviewError("image exceeds preview file size limit")
        data = path.read_bytes()
        after = path.stat()
        if (
            len(data) != asset.file_size
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
            or hashlib.sha256(data).hexdigest() != asset.fingerprint_sha256
        ):
            raise StillFramePreviewError("image changed since project import")
        device = QBuffer()
        device.setData(QByteArray(data))
        device.open(QIODevice.OpenModeFlag.ReadOnly)
        reader = QImageReader(device)
        reader.setAutoTransform(False)
        dimensions = reader.size()
        if (
            not dimensions.isValid()
            or dimensions.width() != asset.width
            or dimensions.height() != asset.height
            or dimensions.width() * dimensions.height() > _MAX_IMAGE_PIXELS
        ):
            raise StillFramePreviewError("image dimensions differ from project")
        reader.setScaledSize(_cover_size(size.width(), size.height(), asset.width, asset.height))
        image = reader.read()
        device.close()
        if image.isNull():
            raise StillFramePreviewError("image could not be decoded")
        return image
    except StillFramePreviewError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise StillFramePreviewError("image preview input could not be read") from None


def render_still_frame(state: ProjectState, timeline_frame: int) -> QImage:
    """Render an exact HOLD frame to in-memory pixels; caller uses a worker.

    Image composition policy: center-cover, SINGLE fills canvas and DOUBLE
    places V1 on the left and V2 on the right; odd widths give right the extra
    pixel. Fail closed on unqualified effects, invisible clips, narration,
    subtitles or mixed-video frames instead of displaying misleading pixels.
    """
    state.validate()
    if type(timeline_frame) is not int or not 0 <= timeline_frame < state.timeline_end_frame:
        raise StillFramePreviewError("timeline frame is outside image project")
    width, height = state.settings.width, state.settings.height
    if width < 2 or height < 1 or width * height > _MAX_PREVIEW_PIXELS:
        raise StillFramePreviewError("project resolution exceeds still preview limits")
    if state.subtitle is not None or state.narration is not None:
        raise StillFramePreviewError("audio and subtitle composition is not qualified")

    active: dict[str, tuple[Clip, Asset]] = {}
    for track in state.tracks:
        for clip in track.clips:
            if clip.timeline_start.frames <= timeline_frame < clip.timeline_end_frame:
                if not clip.enabled or not track.visible:
                    raise StillFramePreviewError("hidden clips are not qualified for preview")
                if track.track_id not in {"V1", "V2"} or track.track_id in active:
                    raise StillFramePreviewError("unqualified preview track or overlap")
                asset = state.asset(clip.asset_id)
                if asset.media_type != "image" or clip.image_hold_frames is None:
                    raise StillFramePreviewError("preview requires canonical still-image clips")
                if clip.properties != ClipProperties():
                    raise StillFramePreviewError("modified image effects are not qualified")
                active[track.track_id] = (clip, asset)
    if "V1" not in active:
        raise StillFramePreviewError("image timeline contains a gap")
    if len(active) == 1:
        placements = ((active["V1"][1], QRect(0, 0, width, height)),)
    elif len(active) == 2 and "V2" in active:
        half = width // 2
        placements = (
            (active["V1"][1], QRect(0, 0, half, height)),
            (active["V2"][1], QRect(half, 0, width - half, height)),
        )
    else:
        raise StillFramePreviewError("image lane layout is unsupported")

    result = QImage(width, height, QImage.Format.Format_ARGB32)
    if result.isNull():
        raise StillFramePreviewError("preview allocation failed")
    result.fill(Qt.GlobalColor.black)
    painter = QPainter(result)
    try:
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        for asset, destination in placements:
            decoded = _decode_verified(asset, destination.size())
            source = QRect(
                (decoded.width() - destination.width()) // 2,
                (decoded.height() - destination.height()) // 2,
                destination.width(),
                destination.height(),
            )
            painter.drawImage(destination, decoded, source)
    finally:
        painter.end()
    return result
