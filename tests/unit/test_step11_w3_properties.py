from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.properties import (
    InspectorTargetType,
    PropertyController,
    PropertyEditError,
    PropertyIntentRouter,
)
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.domain import (
    Asset,
    AudioProperties,
    Clip,
    ColorProperties,
    FrameTime,
    ProjectState,
    VideoProperties,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _controller() -> PropertyController:
    bus = CommandBus(ProjectState.create("W3-PROP", "W3 properties", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "9" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    for clip in (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30)),
        Clip("C002", "A001", FrameTime(120, 30), FrameTime(120, 30), FrameTime(240, 30)),
    ):
        bus.execute(
            CommandBatch(
                f"B{bus.state.revision + 1}",
                "clip",
                "manual",
                bus.state.revision,
                (AddClipCommand(clip),),
            )
        )
    return PropertyController(bus)


def test_inspector_binding_changes_context_without_mutating_project() -> None:
    controller = _controller()
    revision = controller.state.revision

    assert controller.bind_project().target_type is InspectorTargetType.PROJECT
    assert controller.bind_track("V1").target_type is InspectorTargetType.TRACK
    assert controller.bind_asset("A001").target_type is InspectorTargetType.ASSET
    binding = controller.bind_clip("C001")

    assert binding.target_type is InspectorTargetType.CLIP
    assert binding.target_id == "C001"
    assert binding.editable is True
    assert controller.state.revision == revision


def test_video_audio_color_are_undoable_and_persisted(tmp_path: Path) -> None:
    controller = _controller()
    controller.bind_clip("C001")
    before = controller.state.semantic_hash()

    controller.set_video(
        VideoProperties(
            position_x=24,
            position_y=-12,
            scale_x_percent=85,
            scale_y_percent=85,
            rotation_tenths=75,
            opacity_percent=82,
            crop_left_percent=5,
            crop_top_percent=4,
            crop_right_percent=3,
            crop_bottom_percent=2,
        )
    )
    controller.set_audio(
        AudioProperties(volume_percent=72, pan_percent=-25, fade_in_frames=12, fade_out_frames=15)
    )
    controller.set_color(
        ColorProperties(
            brightness_percent=8,
            exposure_tenths_ev=4,
            contrast_percent=15,
            saturation_percent=20,
            temperature_percent=10,
            tint_percent=-8,
        )
    )
    after = controller.state.semantic_hash()
    assert after != before
    assert controller.state.clip("C001").properties.video.opacity_percent == 82
    assert controller.state.clip("C001").properties.audio.pan_percent == -25
    assert controller.state.clip("C001").properties.color.saturation_percent == 20

    controller.undo()
    assert controller.state.clip("C001").properties.color == ColorProperties()
    controller.redo()
    assert controller.state.clip("C001").properties.color.saturation_percent == 20

    path = tmp_path / "w3.angproj"
    repository = JsonProjectRepository()
    repository.save(controller.state, path)
    loaded = repository.load(path)
    assert loaded.semantic_hash() == controller.state.semantic_hash()
    assert loaded.clip("C001").properties.video.position_x == 24


def test_speed_recomputes_duration_and_ripples_later_clips() -> None:
    controller = _controller()
    controller.bind_clip("C001")

    controller.set_speed(200)
    first = controller.state.clip("C001")
    second = controller.state.clip("C002")
    assert first.duration_frames == 60
    assert second.timeline_start.frames == 60
    assert controller.state.timeline_end_frame == 180

    speed_hash = controller.state.semantic_hash()
    controller.undo()
    assert controller.state.clip("C001").duration_frames == 120
    assert controller.state.clip("C002").timeline_start.frames == 120
    controller.redo()
    assert controller.state.semantic_hash() == speed_hash


def test_reverse_is_explicitly_disabled_and_does_not_mutate_state() -> None:
    controller = _controller()
    controller.bind_clip("C001")
    before = controller.state.semantic_hash()

    assert controller.capabilities.reverse_supported is False
    with pytest.raises(PropertyEditError, match="Reverse belum lolos qualification"):
        controller.set_reverse(True)
    assert controller.state.semantic_hash() == before


def test_property_router_uses_semantic_intents() -> None:
    controller = _controller()
    router = PropertyIntentRouter(controller)

    router(
        UiIntent(
            UiIntentType.PROPERTY_SET_SPEED,
            (("clip_id", "C001"), ("rate_percent", "50"), ("ripple", "true")),
        )
    )
    assert controller.state.clip("C001").properties.speed.rate_percent == 50
    assert controller.state.clip("C001").duration_frames == 240
    assert controller.state.clip("C002").timeline_start.frames == 240

    router(
        UiIntent(
            UiIntentType.PROPERTY_SET_VIDEO,
            (
                ("clip_id", "C001"),
                ("position_x", "33"),
                ("scale_x_percent", "90"),
                ("scale_y_percent", "90"),
            ),
        )
    )
    assert controller.state.clip("C001").properties.video.position_x == 33
