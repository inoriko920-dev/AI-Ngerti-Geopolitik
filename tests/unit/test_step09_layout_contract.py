from ai_ngerti_geopolitik.presentation.layout_contract import ShellGeometry


def test_reference_viewport_zones_do_not_overlap() -> None:
    geometry = ShellGeometry.calculate(1920, 1080)
    assert geometry.preview.w >= 640
    assert geometry.left.w > 0
    assert geometry.right.w > 0
    assert geometry.timeline.h >= 180
    assert not geometry.left.intersects(geometry.preview)
    assert not geometry.preview.intersects(geometry.right)
    assert not geometry.timeline.intersects(geometry.left)


def test_compact_viewport_preserves_preview_and_timeline() -> None:
    geometry = ShellGeometry.calculate(1366, 768)
    assert geometry.preview.w >= 640
    assert geometry.timeline.h >= 180
    assert geometry.content.h > geometry.timeline.h
