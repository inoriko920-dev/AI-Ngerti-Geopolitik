"""Deterministic and bounded Scenario DOCX Axxx asset-folder binding tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_asset_bindings import (
    SceneAssetScanError,
    SceneAssetStatus,
)
from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import scan_scene_asset_folder


def plan():
    return parse_scene_docx_lines(
        (
            "Tampilan Scene 1: 1",
            "Asset 1: historical map",
            "Tampilan Scene 2: 2",
            "Asset 2: delegate portrait",
            "Asset 3: flag background",
        )
    )


def make_image(path: Path, fmt: str = "PNG") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = QImage(4, 4, QImage.Format.Format_RGB32)
    image.fill(0x00228844)
    assert image.save(str(path), fmt)


def test_exact_case_insensitive_canonical_names_and_nested_supported_images(
    tmp_path: Path,
) -> None:
    make_image(tmp_path / "A001.png")
    make_image(tmp_path / "subfolder" / "a002.JPG", "JPEG")
    make_image(tmp_path / "A003.webp", "WEBP")
    (tmp_path / "A001-more.png").write_bytes(b"not a canonical match")
    result = scan_scene_asset_folder(plan(), tmp_path)
    assert result.all_ready
    assert result.ready_count == 3
    assert [x.status for x in result.bindings] == [SceneAssetStatus.READY] * 3
    assert [x.asset_id for x in result.bindings] == ["A001", "A002", "A003"]
    assert all(x.path is not None and x.path.is_file() for x in result.bindings)


def test_missing_corrupt_and_unsupported_media_never_claim_ready(tmp_path: Path) -> None:
    (tmp_path / "A001.png").write_bytes(b"not an image")
    (tmp_path / "A002.gif").write_bytes(b"GIF89a not supported")
    result = scan_scene_asset_folder(plan(), tmp_path)
    assert [x.status for x in result.bindings] == [
        SceneAssetStatus.CORRUPT,
        SceneAssetStatus.UNSUPPORTED,
        SceneAssetStatus.MISSING,
    ]
    assert result.ready_count == 0
    assert len(result.blockers) == 3
    assert all(x.path is None for x in result.bindings)


def test_duplicate_even_when_one_variant_is_corrupt_never_auto_selects(
    tmp_path: Path,
) -> None:
    make_image(tmp_path / "A001.png")
    (tmp_path / "deep").mkdir()
    (tmp_path / "deep" / "a001.JPG").write_bytes(b"broken")
    result = scan_scene_asset_folder(plan(), tmp_path)
    first = result.bindings[0]
    assert first.status is SceneAssetStatus.DUPLICATE
    assert first.path is None
    assert len(first.candidates) == 2


def test_zero_byte_media_is_corrupt_not_ready(tmp_path: Path) -> None:
    (tmp_path / "A001.jpg").write_bytes(b"")
    result = scan_scene_asset_folder(plan(), tmp_path)
    assert result.bindings[0].status is SceneAssetStatus.CORRUPT


def test_symlink_files_and_symlinked_folders_are_not_followed(tmp_path: Path) -> None:
    outside = tmp_path.parent / (tmp_path.name + "_outside")
    outside.mkdir()
    make_image(outside / "A001.png")
    try:
        (tmp_path / "A001.png").symlink_to(outside / "A001.png")
        (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink privileges unavailable on Windows runner")
    result = scan_scene_asset_folder(plan(), tmp_path)
    assert result.bindings[0].status is SceneAssetStatus.MISSING


def test_bound_limit_fails_closed_instead_of_reporting_missing(tmp_path: Path) -> None:
    make_image(tmp_path / "A001.png")
    for i in range(6):
        (tmp_path / f"unrelated_{i}.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SceneAssetScanError, match="scan limit"):
        scan_scene_asset_folder(plan(), tmp_path, max_files=2)


def test_invalid_folder_and_limits_are_fixed_privacy_safe_errors(tmp_path: Path) -> None:
    missing = tmp_path / "SECRET_PRIVATE_NOT_EXIST"
    for folder, bounds in ((missing, {}), (tmp_path, {"max_files": 0})):
        with pytest.raises(SceneAssetScanError) as exc:
            scan_scene_asset_folder(plan(), folder, **bounds)
        assert str(folder) not in str(exc.value)
        assert "SECRET_PRIVATE" not in str(exc.value)


def test_verified_images_have_real_hash_and_dimensions(tmp_path: Path) -> None:
    import hashlib

    from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
        require_unchanged_scene_images,
        verify_scene_image_media,
    )

    for number in (1, 2, 3):
        make_image(tmp_path / f"A{number:03d}.png")
    inventory = scan_scene_asset_folder(plan(), tmp_path)
    snapshot = verify_scene_image_media(inventory)
    assert len(snapshot.images) == 3
    assert [x.asset_id for x in snapshot.images] == ["A001", "A002", "A003"]
    for image in snapshot.images:
        assert image.fingerprint_sha256 == hashlib.sha256(image.path.read_bytes()).hexdigest()
        assert image.file_size == image.path.stat().st_size
        assert (image.width, image.height) == (4, 4)
    assert require_unchanged_scene_images(inventory, snapshot) == snapshot


def test_changed_image_after_scan_fails_closed(tmp_path: Path) -> None:
    from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
        require_unchanged_scene_images,
        verify_scene_image_media,
    )

    for number in (1, 2, 3):
        make_image(tmp_path / f"A{number:03d}.png")
    inventory = scan_scene_asset_folder(plan(), tmp_path)
    original = verify_scene_image_media(inventory)
    new_image = QImage(6, 5, QImage.Format.Format_RGB32)
    new_image.fill(0x00DD4422)
    assert new_image.save(str(tmp_path / "A001.png"), "PNG")
    with pytest.raises(SceneAssetScanError, match="changed since preflight"):
        require_unchanged_scene_images(inventory, original)


def test_removed_or_corrupted_image_is_redacted_error(tmp_path: Path) -> None:
    from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
        verify_scene_image_media,
    )

    for number in (1, 2, 3):
        make_image(tmp_path / f"A{number:03d}.png")
    inventory = scan_scene_asset_folder(plan(), tmp_path)
    target = tmp_path / "A002.png"
    target.unlink()
    with pytest.raises(SceneAssetScanError) as err:
        verify_scene_image_media(inventory)
    assert str(tmp_path) not in str(err.value)
    target.write_bytes(b"invalid private image")
    with pytest.raises(SceneAssetScanError, match="no longer decodes"):
        verify_scene_image_media(inventory)


def test_oversize_or_incomplete_image_inventory_is_blocked(tmp_path: Path) -> None:
    from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
        verify_scene_image_media,
    )

    make_image(tmp_path / "A001.png")
    incomplete = scan_scene_asset_folder(plan(), tmp_path)
    with pytest.raises(SceneAssetScanError, match="blockers"):
        verify_scene_image_media(incomplete)
    for number in (2, 3):
        make_image(tmp_path / f"A{number:03d}.png")
    ready = scan_scene_asset_folder(plan(), tmp_path)
    with pytest.raises(SceneAssetScanError, match="size"):
        verify_scene_image_media(ready, max_image_bytes=1)
    with pytest.raises(SceneAssetScanError, match="size"):
        verify_scene_image_media(ready, max_image_bytes=0)


def test_depth_limit_rejects_unscanned_nested_duplicate_not_false_ready(
    tmp_path: Path,
) -> None:
    for number in (1, 2, 3):
        make_image(tmp_path / f"A{number:03d}.png")
    deepest = tmp_path / "first" / "second" / "third"
    deepest.mkdir(parents=True)
    make_image(deepest / "A001.png")
    with pytest.raises(SceneAssetScanError, match="scan depth"):
        scan_scene_asset_folder(plan(), tmp_path, max_depth=2)
    # Increasing the limit must reveal the duplicate, not choose either copy.
    inventory = scan_scene_asset_folder(plan(), tmp_path, max_depth=5)
    assert inventory.bindings[0].status is SceneAssetStatus.DUPLICATE
    assert not inventory.all_ready

