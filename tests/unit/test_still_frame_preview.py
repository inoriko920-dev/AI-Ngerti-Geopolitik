"""Actual Qt image frame compositing from saved canonical .angproj; no native engine."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.bootstrap.scene_cli import main as import_cli_main
from ai_ngerti_geopolitik.domain import FrameTime
from ai_ngerti_geopolitik.domain.properties import (
    ClipProperties,
    EffectProperties,
    TransitionProperties,
    VideoProperties,
)
from ai_ngerti_geopolitik.infrastructure.mlt_projection import (
    MltProjectionError,
    build_mlt_timeline_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_preview import (
    StillFramePreviewError,
    render_still_frame,
)


def _save_real_project(tmp_path: Path):
    docx = parse_scene_docx_lines(
        (
            "Scene 1: 1",
            "Asset 1: Red image",
            "Scene 2: 2",
            "Asset 2: Green image",
            "Asset 3: Blue image",
        )
    )
    for number, rgb in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(rgb)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-PREVIEW",
        project_name="Preview",
    )
    state = replace(state, settings=replace(state.settings, width=13, height=8))
    path = tmp_path / "preview.angproj"
    repo = JsonProjectRepository()
    repo.save(state, path)
    return repo.load(path)


@pytest.mark.parametrize("frame", [0, 1, 149])
def test_single_is_real_red_full_canvas_at_every_hold_frame(tmp_path: Path, frame: int) -> None:
    state = _save_real_project(tmp_path)
    image = render_still_frame(state, frame)
    assert (image.width(), image.height()) == (13, 8)
    for x in range(13):
        for y in (0, 4, 7):
            assert image.pixelColor(x, y).name() == "#ff0000"


@pytest.mark.parametrize("frame", [150, 151, 239])
def test_double_is_real_green_left_blue_right_parallel(tmp_path: Path, frame: int) -> None:
    image = render_still_frame(_save_real_project(tmp_path), frame)
    assert image.pixelColor(0, 2).name() == "#00ff00"
    assert image.pixelColor(5, 2).name() == "#00ff00"
    assert image.pixelColor(6, 2).name() == "#0000ff"
    assert image.pixelColor(12, 7).name() == "#0000ff"


def test_deleted_or_changed_file_blocks_preview_with_no_user_path(
    tmp_path: Path,
) -> None:
    state = _save_real_project(tmp_path)
    (tmp_path / "A002.png").write_bytes(b"private broken input")
    with pytest.raises(StillFramePreviewError) as error:
        render_still_frame(state, 150)
    assert str(tmp_path) not in str(error.value)


def test_unapproved_transform_never_silently_ignored(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    current = state.tracks[0].clips[0]
    changed = replace(
        current,
        properties=ClipProperties(video=VideoProperties(position_x=12)),
    )
    modified = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(changed, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(modified, 0)


def test_missing_lane_and_out_of_range_do_not_render_wrong_pixels(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    for frame in (-1, 240, True):
        with pytest.raises(StillFramePreviewError, match="outside"):
            render_still_frame(state, frame)
    empty = replace(state, tracks=(state.tracks[1],))
    with pytest.raises(StillFramePreviewError, match="gap"):
        render_still_frame(empty, 0)


def test_mlt_native_preview_remains_blocked_separately(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    with pytest.raises(MltProjectionError, match="requires video assets"):
        build_mlt_timeline_plan(state)


def test_image_intrinsic_frame_stays_one_across_hold(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    assert state.clip("SCENE-0001-A001").source_frame_at_timeline_offset(149) == 0
    assert state.asset("A001").duration == FrameTime(1, 30)


def test_cli_outputs_real_preview_png_and_refuses_overwrite(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    project = tmp_path / "preview.angproj"
    output = tmp_path / "frame_150.png"
    assert state.timeline_end_frame == 240
    args = ["preview", "--project", str(project), "--frame", "150", "--output", str(output)]
    assert import_cli_main(args) == 0
    saved = QImage(str(output))
    assert not saved.isNull()
    assert (saved.width(), saved.height()) == (13, 8)
    assert saved.pixelColor(0, 1).name() == "#00ff00"
    assert saved.pixelColor(12, 1).name() == "#0000ff"
    assert import_cli_main(args) == 1
    invalid_args = [
        "preview",
        "--project",
        str(project),
        "--frame",
        "240",
        "--output",
        str(tmp_path / "outside.png"),
    ]
    assert import_cli_main(invalid_args) == 1
    assert not (tmp_path / "outside.png").exists()


def test_v1_fade_black_has_black_opening_full_middle_and_faded_closing(
    tmp_path: Path,
) -> None:
    state = _save_real_project(tmp_path)
    first = state.tracks[0].clips[0]
    faded = replace(
        first,
        properties=replace(
            first.properties,
            transition=TransitionProperties("fade_black", 15),
        ),
    )
    project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(faded, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    project.validate()
    assert render_still_frame(project, 0).pixelColor(3, 3).red() <= 1
    assert 100 <= render_still_frame(project, 7).pixelColor(3, 3).red() <= 145
    assert render_still_frame(project, 40).pixelColor(3, 3).red() >= 250
    assert render_still_frame(project, 149).pixelColor(3, 3).red() < 35
    assert render_still_frame(project, 150).pixelColor(3, 3).green() >= 250


def test_fade_in_double_scene_and_other_motion_effects_reject_without_fake_pixels(
    tmp_path: Path,
) -> None:
    state = _save_real_project(tmp_path)
    second = state.tracks[0].clips[1]
    faded_double = replace(
        second,
        properties=replace(second.properties, transition=TransitionProperties("fade_black", 8)),
    )
    double_state = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(state.tracks[0].clips[0], faded_double)),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="single V1"):
        render_still_frame(double_state, 150)
    unsupported = replace(
        state.tracks[0].clips[0],
        properties=replace(
            state.tracks[0].clips[0].properties,
            effects=EffectProperties(enter_effect="Pop"),
        ),
    )
    unsupported_state = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(unsupported, state.tracks[0].clips[1])),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(unsupported_state, 0)


def test_w4_fade_enter_exit_uses_frame_exact_alpha_not_static_image(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    first = state.tracks[0].clips[0]
    animated = replace(
        first,
        properties=replace(
            first.properties,
            effects=EffectProperties(enter_effect="Fade", exit_effect="Fade"),
        ),
    )
    project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(animated, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    project.validate()
    assert render_still_frame(project, 0).pixelColor(3, 3).red() == 0
    assert 100 <= render_still_frame(project, 4).pixelColor(3, 3).red() <= 150
    assert render_still_frame(project, 20).pixelColor(3, 3).red() >= 250
    assert render_still_frame(project, 149).pixelColor(3, 3).red() < 50
    assert render_still_frame(project, 150).pixelColor(0, 3).green() >= 250


def test_w4_fade_only_enter_and_only_exit_preserve_other_end(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    first = state.tracks[0].clips[0]
    for incoming, outgoing in (("Fade", "None"), ("None", "Fade")):
        changed = replace(
            first,
            properties=replace(
                first.properties,
                effects=EffectProperties(enter_effect=incoming, exit_effect=outgoing),
            ),
        )
        project = replace(
            state,
            tracks=(
                replace(state.tracks[0], clips=(changed, *state.tracks[0].clips[1:])),
                state.tracks[1],
            ),
        )
        opening = render_still_frame(project, 0).pixelColor(2, 2).red()
        ending = render_still_frame(project, 149).pixelColor(2, 2).red()
        if incoming == "Fade":
            assert opening == 0
            assert ending >= 250
        else:
            assert opening >= 250
            assert ending < 50


def test_w4_fade_still_rejects_unqualified_combination_and_double_lane(
    tmp_path: Path,
) -> None:
    state = _save_real_project(tmp_path)
    first = state.tracks[0].clips[0]
    combined = replace(
        first,
        properties=replace(
            first.properties,
            transition=TransitionProperties("fade_black", 10),
            effects=EffectProperties(enter_effect="Fade"),
        ),
    )
    bad = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(combined, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(bad, 0)

    double = replace(
        state.tracks[0].clips[1],
        properties=replace(
            state.tracks[0].clips[1].properties,
            effects=EffectProperties(enter_effect="Fade"),
        ),
    )
    bad_double = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(first, double)),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="single V1"):
        render_still_frame(bad_double, 150)


def _pan_pattern_state(tmp_path: Path):
    state = _save_real_project(tmp_path)
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    for x in range(64):
        color = QColor((x * 4) % 256, (x * 7) % 256, (x * 11) % 256)
        for y in range(48):
            image.setPixelColor(x, y, color)
    source = tmp_path / "A001.png"
    assert image.save(str(source), "PNG")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assets = tuple(
        replace(
            asset,
            width=64,
            height=48,
            file_size=source.stat().st_size,
            fingerprint_sha256=digest,
        )
        if asset.asset_id == "A001"
        else asset
        for asset in state.assets
    )
    state = replace(
        state,
        assets=assets,
        settings=replace(state.settings, width=128, height=72),
    )
    state.validate()
    return state


def test_w4_pan_in_out_moves_real_pattern_without_black_borders(tmp_path: Path) -> None:
    state = _pan_pattern_state(tmp_path)
    first = state.tracks[0].clips[0]
    moved = replace(
        first,
        properties=replace(
            first.properties,
            effects=EffectProperties(enter_effect="Pan", exit_effect="Pan"),
        ),
    )
    state = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(moved, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    state.validate()
    frames = [render_still_frame(state, f) for f in (0, 4, 18, 147, 149)]
    assert all((image.width(), image.height()) == (128, 72) for image in frames)

    def pixels(image: QImage) -> tuple[int, ...]:
        return tuple(image.pixelColor(x, 36).red() for x in range(12, 117, 5))

    start, entering, settled, leaving, end = (pixels(image) for image in frames)

    def difference(a: tuple[int, ...], b: tuple[int, ...]) -> int:
        return sum(abs(x - y) for x, y in zip(a, b, strict=True))

    assert difference(start, settled) > 30
    assert difference(entering, settled) > 10
    assert difference(leaving, settled) > 10
    assert difference(end, settled) > 30
    # Even the first/last moved frame covers the whole canvas with source pixels.
    for image in frames:
        for x in (0, 64, 127):
            assert image.pixelColor(x, 36).alpha() == 255


def test_w4_pan_double_scene_or_combined_fade_fails_closed(tmp_path: Path) -> None:
    state = _pan_pattern_state(tmp_path)
    second = state.tracks[0].clips[1]
    bad_double = replace(
        second,
        properties=replace(
            second.properties,
            effects=EffectProperties(enter_effect="Pan"),
        ),
    )
    double_project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(state.tracks[0].clips[0], bad_double)),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="single V1"):
        render_still_frame(double_project, 151)
    first = state.tracks[0].clips[0]
    combined = replace(
        first,
        properties=replace(
            first.properties,
            effects=EffectProperties(enter_effect="Pan", exit_effect="Fade"),
        ),
    )
    invalid = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(combined, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(invalid, 0)


def _drift_pattern_state(tmp_path: Path):
    """Color varies independently with X and Y to prove diagonal movement."""
    state = _pan_pattern_state(tmp_path)
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    for x in range(64):
        for y in range(48):
            image.setPixelColor(
                x,
                y,
                QColor(
                    (4 * x + 2 * y + 40) % 256,
                    (2 * x + 5 * y + 30) % 256,
                    (3 * x + 7 * y + 20) % 256,
                ),
            )
    source = tmp_path / "A001.png"
    assert image.save(str(source), "PNG")
    checksum = hashlib.sha256(source.read_bytes()).hexdigest()
    media = tuple(
        replace(asset, file_size=source.stat().st_size, fingerprint_sha256=checksum)
        if asset.asset_id == "A001"
        else asset
        for asset in state.assets
    )
    changed = replace(state, assets=media)
    changed.validate()
    return changed


def test_w4_drift_moves_diagonally_in_out_without_exposed_canvas(tmp_path: Path) -> None:
    state = _drift_pattern_state(tmp_path)
    clip = state.tracks[0].clips[0]
    moved = replace(
        clip,
        properties=replace(
            clip.properties,
            effects=EffectProperties(enter_effect="Drift", exit_effect="Drift"),
        ),
    )
    state = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(moved, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    state.validate()
    frames = [render_still_frame(state, frame) for frame in (0, 4, 18, 147, 149)]
    assert all((image.width(), image.height()) == (128, 72) for image in frames)

    def samples(image: QImage) -> tuple[int, ...]:
        return tuple(
            component
            for x, y in ((15, 14), (64, 36), (105, 56))
            for component in (
                image.pixelColor(x, y).red(),
                image.pixelColor(x, y).green(),
                image.pixelColor(x, y).blue(),
            )
        )

    start, entering, settled, leaving, end = (samples(frame) for frame in frames)

    def delta(left: tuple[int, ...], right: tuple[int, ...]) -> int:
        return sum(abs(x - y) for x, y in zip(left, right, strict=True))

    assert delta(start, settled) > 50
    assert delta(entering, settled) > 15
    assert delta(leaving, settled) > 15
    assert delta(end, settled) > 50
    for image in frames:
        assert image.pixelColor(0, 0).alpha() == 255
        assert image.pixelColor(127, 71).alpha() == 255


@pytest.mark.parametrize(
    ("enter", "exit"),
    [("Drift", "Fade"), ("Pan", "Drift"), ("Drift", "Pan")],
)
def test_w4_drift_mixed_effects_rejected(tmp_path: Path, enter: str, exit: str) -> None:
    state = _drift_pattern_state(tmp_path)
    first = state.tracks[0].clips[0]
    invalid = replace(
        first,
        properties=replace(
            first.properties, effects=EffectProperties(enter_effect=enter, exit_effect=exit)
        ),
    )
    project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(invalid, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(project, 0)


def test_w4_drift_rejects_double_lane_and_transition(tmp_path: Path) -> None:
    state = _drift_pattern_state(tmp_path)
    second = state.tracks[0].clips[1]
    double = replace(
        second,
        properties=replace(second.properties, effects=EffectProperties(enter_effect="Drift")),
    )
    project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(state.tracks[0].clips[0], double)),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="single V1"):
        render_still_frame(project, 151)
    first = state.tracks[0].clips[0]
    both = replace(
        first,
        properties=replace(
            first.properties,
            transition=TransitionProperties("fade_black", 8),
            effects=EffectProperties(enter_effect="Drift"),
        ),
    )
    invalid = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(both, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(invalid, 0)



def test_w4_rise_moves_vertical_pixels_in_out_without_exposed_borders(tmp_path: Path) -> None:
    state = _drift_pattern_state(tmp_path)
    clip = state.tracks[0].clips[0]
    moved = replace(
        clip,
        properties=replace(
            clip.properties,
            effects=EffectProperties(enter_effect="Rise", exit_effect="Rise"),
        ),
    )
    project = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(moved, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    project.validate()
    images = [render_still_frame(project, index) for index in (0, 4, 18, 147, 149)]
    assert all((image.width(), image.height()) == (128, 72) for image in images)

    def pixels(image: QImage) -> tuple[int, ...]:
        return tuple(
            component
            for x, y in ((15, 14), (64, 36), (105, 56))
            for component in (
                image.pixelColor(x, y).red(),
                image.pixelColor(x, y).green(),
                image.pixelColor(x, y).blue(),
            )
        )

    start, entering, middle, leaving, end = (pixels(image) for image in images)

    def deviation(a: tuple[int, ...], b: tuple[int, ...]) -> int:
        return sum(abs(x - y) for x, y in zip(a, b, strict=True))

    assert deviation(start, middle) > 35
    assert deviation(entering, middle) > 10
    assert deviation(leaving, middle) > 10
    assert deviation(end, middle) > 35
    for image in images:
        assert image.pixelColor(0, 0).alpha() == 255
        assert image.pixelColor(127, 71).alpha() == 255


@pytest.mark.parametrize(("enter", "exit"), [("Rise", "Pan"), ("Drift", "Rise"), ("Fade", "Rise")])
def test_w4_rise_mixed_effects_fail_closed(
    tmp_path: Path, enter: str, exit: str
) -> None:
    state = _drift_pattern_state(tmp_path)
    first = state.tracks[0].clips[0]
    bad = replace(
        first,
        properties=replace(
            first.properties,
            effects=EffectProperties(enter_effect=enter, exit_effect=exit),
        ),
    )
    invalid = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(bad, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(invalid, 0)


def test_w4_rise_rejects_double_lane_and_fade_black_transition(tmp_path: Path) -> None:
    state = _drift_pattern_state(tmp_path)
    second = state.tracks[0].clips[1]
    animated = replace(
        second,
        properties=replace(second.properties, effects=EffectProperties(enter_effect="Rise")),
    )
    double = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(state.tracks[0].clips[0], animated)),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="single V1"):
        render_still_frame(double, 151)
    first = state.tracks[0].clips[0]
    combined = replace(
        first,
        properties=replace(
            first.properties,
            transition=TransitionProperties("fade_black", 8),
            effects=EffectProperties(enter_effect="Rise"),
        ),
    )
    invalid = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(combined, *state.tracks[0].clips[1:])),
            *state.tracks[1:],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(invalid, 0)
