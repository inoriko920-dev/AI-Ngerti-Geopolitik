from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.creative import (
    CreativeController,
    CreativeEditError,
    CreativeIntentRouter,
)
from ai_ngerti_geopolitik.application.ui_intents import (
    UiIntent,
    UiIntentType,
)
from ai_ngerti_geopolitik.domain import (
    UNSUPPORTED_LEGACY_EFFECTS,
    Asset,
    Clip,
    EffectProperties,
    FrameTime,
    ProjectState,
    TitleProperties,
    TransitionProperties,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_creative import (
    build_w4_creative_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
)


def _controller() -> CreativeController:
    bus = CommandBus(ProjectState.create("W4-CREATIVE", "W4 creative", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "8" * 64,
    )
    bus.execute(
        CommandBatch(
            "B1",
            "import",
            "manual",
            0,
            (ImportAssetCommand(asset),),
        )
    )
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(120, 30),
    )
    bus.execute(
        CommandBatch(
            "B2",
            "clip",
            "manual",
            bus.state.revision,
            (AddClipCommand(clip),),
        )
    )
    controller = CreativeController(bus)
    controller.bind_clip("C001")
    return controller


def test_w4_creative_state_is_undoable_and_persisted(
    tmp_path: Path,
) -> None:
    controller = _controller()
    baseline = controller.state.semantic_hash()

    controller.set_title(
        TitleProperties(
            enabled=True,
            text="GEOPOLITIK",
            font_size=72,
            position="bottom",
            background_opacity_percent=60,
        )
    )
    controller.set_transition(TransitionProperties("fade_black", 12))
    controller.set_effects(
        EffectProperties(
            enter_effect="Rise",
            exit_effect="Fade",
            intensity_percent=120,
            locked=True,
        )
    )
    creative_hash = controller.state.semantic_hash()
    assert creative_hash != baseline
    clip = controller.state.clip("C001")
    assert clip.properties.title.text == "GEOPOLITIK"
    assert clip.properties.transition.preset == "fade_black"
    assert clip.properties.effects.enter_effect == "Rise"

    for _ in range(3):
        controller.undo()
    assert controller.state.semantic_hash() == baseline
    for _ in range(3):
        controller.redo()
    assert controller.state.semantic_hash() == creative_hash

    path = tmp_path / "w4.angproj"
    repository = JsonProjectRepository()
    repository.save(controller.state, path)
    loaded = repository.load(path)
    assert loaded.semantic_hash() == creative_hash
    assert loaded.clip("C001").properties.effects.locked is True


def test_w4_transition_cannot_exceed_half_clip() -> None:
    controller = _controller()
    with pytest.raises(CreativeEditError, match="half"):
        controller.set_transition(TransitionProperties("fade_black", 61))


def test_w4_ffmpeg_plan_contains_real_creative_mapping() -> None:
    controller = _controller()
    controller.set_title(
        TitleProperties(
            enabled=True,
            text="ANG",
            position="center",
        )
    )
    controller.set_transition(TransitionProperties("fade_black", 12))
    controller.set_effects(
        EffectProperties(
            enter_effect="Rise",
            exit_effect="Fade",
            intensity_percent=100,
        )
    )
    plan = build_w4_creative_plan(
        controller.state.clip("C001"),
        30,
        base_x="(main_w-overlay_w)/2",
        base_y="(main_h-overlay_h)/2",
    )

    assert plan.overlay_y != "(main_h-overlay_h)/2"
    assert any(item.startswith("drawtext=") for item in plan.post_filters)
    assert sum(item.startswith("fade=t=") for item in plan.post_filters) == 2
    assert any("alpha=1" in item for item in plan.source_filters)
    assert "Wipe" in UNSUPPORTED_LEGACY_EFFECTS


def test_w4_router_uses_semantic_intents() -> None:
    controller = _controller()
    router = CreativeIntentRouter(controller)

    router(
        UiIntent(
            UiIntentType.CREATIVE_SET_TITLE,
            (
                ("clip_id", "C001"),
                ("enabled", "true"),
                ("text", "Judul"),
                ("font_size", "64"),
                ("position", "top"),
            ),
        )
    )
    assert controller.state.clip("C001").properties.title.text == "Judul"

    router(
        UiIntent(
            UiIntentType.CREATIVE_SET_EFFECTS,
            (
                ("clip_id", "C001"),
                ("enter_effect", "Pan"),
                ("exit_effect", "Drift"),
                ("intensity_percent", "90"),
                ("locked", "true"),
            ),
        )
    )
    effects = controller.state.clip("C001").properties.effects
    assert effects.enter_effect == "Pan"
    assert effects.exit_effect == "Drift"
    assert effects.locked is True
