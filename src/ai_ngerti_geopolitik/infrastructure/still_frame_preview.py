"""CPU/Qt still-frame preview for canonical image clips (worker-only).

This adapter renders SINGLE/DOUBLE image HOLD frames and a qualified V1-only
fade-through-black, W4 Fade/Pan/Drift/Rise, Breathe, Pop, or Stomp.
All unsupported combinations fail closed.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRect, QSize, Qt
from PySide6.QtGui import QColor, QImage, QImageReader, QPainter

from ai_ngerti_geopolitik.domain import Asset, Clip, ProjectState
from ai_ngerti_geopolitik.domain.still_animation import (
    qualified_still_breathe,
    qualified_still_drift,
    qualified_still_pan,
    qualified_still_pop,
    qualified_still_rise,
    qualified_still_stomp,
    qualified_still_visibility,
)

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
                try:
                    qualified_still_visibility(clip, timeline_frame)
                except ValueError:
                    raise StillFramePreviewError(
                        "modified image effects are not qualified"
                    ) from None
                if (
                    clip.properties.transition.preset == "fade_black"
                    or clip.properties.effects.enter_effect == "Fade"
                    or clip.properties.effects.exit_effect == "Fade"
                    or clip.properties.effects.enter_effect == "Pan"
                    or clip.properties.effects.exit_effect == "Pan"
                    or clip.properties.effects.enter_effect == "Drift"
                    or clip.properties.effects.exit_effect == "Drift"
                    or clip.properties.effects.enter_effect == "Rise"
                    or clip.properties.effects.exit_effect == "Rise"
                    or clip.properties.effects.enter_effect == "Breathe"
                    or clip.properties.effects.exit_effect == "Breathe"
                    or clip.properties.effects.enter_effect == "Pop"
                    or clip.properties.effects.exit_effect == "Pop"
                    or clip.properties.effects.enter_effect == "Stomp"
                    or clip.properties.effects.exit_effect == "Stomp"
                ) and track.track_id != "V1":
                    raise StillFramePreviewError("fade requires the single V1 image lane")
                active[track.track_id] = (clip, asset)
    if "V1" not in active:
        raise StillFramePreviewError("image timeline contains a gap")
    fade = qualified_still_visibility(active["V1"][0], timeline_frame)
    pan = qualified_still_pan(active["V1"][0], timeline_frame)
    drift = qualified_still_drift(active["V1"][0], timeline_frame)
    rise = qualified_still_rise(active["V1"][0], timeline_frame)
    breathe = qualified_still_breathe(active["V1"][0], timeline_frame)
    pop = qualified_still_pop(active["V1"][0], timeline_frame)
    stomp = qualified_still_stomp(active["V1"][0], timeline_frame)
    if (
        any(value is not None for value in (fade, pan, drift, rise, breathe, pop, stomp))
        and len(active) != 1
    ):
        raise StillFramePreviewError(
            "animation requires the single V1 image lane"
        )
    placements: tuple[tuple[Asset, QRect], ...]
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
            requested = destination.size()
            if any(value is not None for value in (pan, drift, rise, breathe, pop, stomp)):
                overscan = (
                    120
                    if pop is not None or stomp is not None
                    else 116
                    if rise is not None
                    else 105
                    if breathe is not None
                    else 112
                )
                requested = QSize(
                    (destination.width() * overscan + 99) // 100,
                    (destination.height() * overscan + 99) // 100,
                )
            decoded = _decode_verified(asset, requested)
            # W4 Breathe crops ~2% more source at its start/end (zoom-out)
            # than midclip. Decode 5% overscan to avoid uncovered borders.
            scale = stomp if stomp is not None else pop if pop is not None else breathe
            crop_width = (
                math.ceil(destination.width() / scale) if scale is not None else destination.width()
            )
            crop_height = (
                math.ceil(destination.height() / scale)
                if scale is not None
                else destination.height()
            )
            if crop_width > decoded.width() or crop_height > decoded.height():
                raise StillFramePreviewError("animation needs unavailable source coverage")
            center_x = (decoded.width() - crop_width) // 2
            center_y = (decoded.height() - crop_height) // 2
            shift_x = round(pan * center_x) if pan is not None else 0
            shift_x += round(drift * center_x) if drift is not None else 0
            shift_y = round(-drift * center_y) if drift is not None else 0
            if rise is not None:
                shift_y -= round(rise * min(center_y, 0.08 * destination.height()))
            source = QRect(
                center_x + shift_x,
                center_y + shift_y,
                crop_width,
                crop_height,
            )
            painter.drawImage(destination, decoded, source)
        if fade is not None and fade < 1.0:
            alpha = max(0, min(255, round(255 * (1.0 - fade))))
            painter.fillRect(result.rect(), QColor(0, 0, 0, alpha))
    finally:
        painter.end()
    return result
