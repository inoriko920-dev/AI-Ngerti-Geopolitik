from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch, CommandBus
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.mlt_projection import (
    MltProjectionError,
    build_mlt_timeline_plan,
)


def _state() -> ProjectState:
    asset = Asset(
        "A001",
        str(Path("D:/media/input.mp4")),
        "video",
        FrameTime(240, 30),
        1280,
        720,
        True,
        "c" * 64,
    )
    state = ProjectState.create("W2-MLT", "MLT projection", 30)
    state = replace(state, assets=(asset,))
    bus = CommandBus(state)
    for clip in (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
        Clip("C002", "A001", FrameTime(60, 30), FrameTime(120, 30), FrameTime(180, 30)),
    ):
        bus.execute(
            CommandBatch(
                f"B{bus.state.revision + 1}",
                "add",
                "manual",
                bus.state.revision,
                (AddClipCommand(clip),),
            )
        )
    return bus.state


def test_mlt_projection_preserves_order_and_source_ranges() -> None:
    plan = build_mlt_timeline_plan(_state())
    assert plan.timeline_end_frame == 120
    assert [segment.clip_id for segment in plan.segments] == ["C001", "C002"]
    assert plan.melt_source_arguments(0) == [
        str(Path("D:/media/input.mp4")),
        "in=0",
        "out=59",
        str(Path("D:/media/input.mp4")),
        "in=120",
        "out=179",
    ]
    assert plan.melt_source_arguments(75) == [
        str(Path("D:/media/input.mp4")),
        "in=135",
        "out=179",
    ]


def test_mlt_projection_blocks_missing_media() -> None:
    state = _state()
    missing = replace(state.asset("A001"), availability="missing")
    blocked = replace(state, assets=(missing,))
    with pytest.raises(MltProjectionError, match="availability=missing"):
        build_mlt_timeline_plan(blocked)
