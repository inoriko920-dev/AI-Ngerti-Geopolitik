"""Bounded, read-only local scan for explicit Scene DOCX Axxx filenames.

Image readiness means a supported format decoded by QImageReader. No untrusted
path guesses, symlink traversal, media copying, or canonical state mutations.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from ai_ngerti_geopolitik.application.scene_asset_bindings import (
    SceneAssetCandidate,
    SceneAssetInventory,
    SceneAssetScanError,
    VerifiedSceneImage,
    VerifiedSceneImageSet,
    bind_scene_asset_candidates,
)
from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxPlan

_SUPPORTED = frozenset({".png", ".jpg", ".jpeg", ".webp"})
_MAX_IMAGE_PIXELS = 100_000_000


def _valid_image(path: Path) -> bool:
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QImageReader

    try:
        if path.stat().st_size <= 0:
            return False
        reader = QImageReader(str(path))
        reader.setAutoTransform(False)
        if not reader.canRead():
            return False
        size = reader.size()
        if not size.isValid() or size.width() * size.height() > _MAX_IMAGE_PIXELS:
            return False
        reader.setScaledSize(QSize(min(size.width(), 64), min(size.height(), 64)))
        image = reader.read()
        return not image.isNull()
    except (OSError, RuntimeError, ValueError):
        return False


def scan_scene_asset_folder(
    plan: SceneDocxPlan,
    root: Path,
    *,
    max_files: int = 2000,
    max_depth: int = 5,
) -> SceneAssetInventory:
    """Inspect at most max_files entries, failing rather than returning partial success."""
    if not 1 <= max_files <= 10000 or not 0 <= max_depth <= 12:
        raise SceneAssetScanError("asset scan limits are invalid")
    try:
        root = root.resolve(strict=True)
        if not root.is_dir():
            raise SceneAssetScanError("asset folder is unavailable")
        expected = {asset.canonical_id for scene in plan.scenes for asset in scene.assets}
        found: list[SceneAssetCandidate] = []
        visited_files = 0
        visited_dirs = 0
        for base, folders, filenames in os.walk(root, topdown=True, followlinks=False):
            visited_dirs += 1
            if visited_dirs > max_files * 4:
                raise SceneAssetScanError("asset folder has too many directories")
            current = Path(base)
            depth = len(current.relative_to(root).parts)
            folders[:] = sorted(
                (
                    name
                    for name in folders
                    if depth < max_depth and not (current / name).is_symlink()
                ),
                key=str.casefold,
            )
            for filename in sorted(filenames, key=lambda x: (x.casefold(), x)):
                visited_files += 1
                if visited_files > max_files:
                    raise SceneAssetScanError("asset folder exceeds scan limit")
                candidate = current / filename
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                if not candidate.resolve().is_relative_to(root):
                    continue
                asset_id = candidate.stem.upper()
                if asset_id not in expected:
                    continue
                supported = candidate.suffix.lower() in _SUPPORTED
                found.append(
                    SceneAssetCandidate(
                        asset_id,
                        candidate.resolve(),
                        supported,
                        supported and _valid_image(candidate),
                    )
                )
        return bind_scene_asset_candidates(plan, tuple(found))
    except SceneAssetScanError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise SceneAssetScanError("asset folder could not be scanned") from None



def verify_scene_image_media(
    inventory: SceneAssetInventory, *, max_image_bytes: int = 128 * 1024 * 1024
) -> VerifiedSceneImageSet:
    """Recheck decoded dimensions and SHA-256 in a worker, before future Save."""
    from PySide6.QtGui import QImageReader

    if not 1 <= max_image_bytes <= 1024 * 1024 * 1024:
        raise SceneAssetScanError("image size limit is invalid")
    if not inventory.all_ready:
        raise SceneAssetScanError("unresolved asset blockers prevent verification")
    verified: list[VerifiedSceneImage] = []
    try:
        for item in inventory.bindings:
            path = item.path
            if (
                path is None
                or len(item.candidates) != 1
                or path.is_symlink()
                or path.suffix.lower() not in _SUPPORTED
                or not path.is_file()
            ):
                raise SceneAssetScanError("image binding changed or is ambiguous")
            before = path.stat()
            if not 0 < before.st_size <= max_image_bytes:
                raise SceneAssetScanError("image size is outside safe limits")
            if not _valid_image(path):
                raise SceneAssetScanError("image no longer decodes")
            size = QImageReader(str(path)).size()
            if (
                not size.isValid()
                or size.width() <= 0
                or size.height() <= 0
                or size.width() * size.height() > _MAX_IMAGE_PIXELS
            ):
                raise SceneAssetScanError("image dimensions are invalid")
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
            after = path.stat()
            if (
                (before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
            ):
                raise SceneAssetScanError("image changed during verification")
            verified.append(
                VerifiedSceneImage(
                    asset_id=item.asset_id,
                    path=path,
                    fingerprint_sha256=digest.hexdigest(),
                    file_size=after.st_size,
                    width=size.width(),
                    height=size.height(),
                )
            )
        return VerifiedSceneImageSet(tuple(verified))
    except SceneAssetScanError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise SceneAssetScanError("image verification failed") from None


def require_unchanged_scene_images(
    inventory: SceneAssetInventory, baseline: VerifiedSceneImageSet
) -> VerifiedSceneImageSet:
    """Reject stale image content, never silently save it as an Axxx binding."""
    current = verify_scene_image_media(inventory)
    if current != baseline:
        raise SceneAssetScanError("image changed since preflight")
    return current
