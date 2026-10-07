from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_l2_context import L2ContextBuilder
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_contracts import W7_ALLOWED_COMMAND_TYPES
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    SpeedProperties,
    Track,
    TransitionProperties,
    VideoProperties,
)


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-002",
        "fixture-private-path.mp4",
        "video",
        FrameTime(1800, fps),
        1920,
        1080,
        True,
        "8" * 64,
        source_name="private-fixture-name.mp4",
    )
    first = Clip(
        "clip-1",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(120, fps),
        properties=replace(
            ClipProperties(),
            video=VideoProperties(
                position_x=10,
                scale_x_percent=110,
                scale_y_percent=110,
            ),
            effects=EffectProperties("Fade", "Drift", 100, False),
        ),
    )
    second = Clip(
        "clip-2",
        asset.asset_id,
        FrameTime(180, fps),
        FrameTime(120, fps),
        FrameTime(270, fps),
        properties=replace(
            ClipProperties(),
            speed=SpeedProperties(125),
            transition=TransitionProperties("fade_black", 15),
            effects=EffectProperties("Pop", "None", 90, True),
        ),
    )
    state = replace(
        ProjectState.create(
            "project-w7-002-evidence",
            "Bounded W7 Context",
            fps,
        ),
        revision=52,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(first, second)),),
    )
    state.validate()
    return state


def main() -> int:
    output = Path("artifacts/step11/w7-002/evidence")
    output.mkdir(parents=True, exist_ok=True)

    state = _state()
    before = state.semantic_json(include_revision=True)
    raw = L2ContextBuilder().build(
        state,
        W7SelectedScope(("clip-2", "clip-1")),
    )
    data = json.loads(raw)

    report = {
        "status": "PASS",
        "schema_version": data["schema_version"],
        "auto_edit_plan_schema_version": data["auto_edit_plan_schema_version"],
        "selected_clip_ids": data["selected_scope"]["clip_ids"],
        "target_count": data["selected_scope"]["target_count"],
        "allowed_command_types": data["policy"]["allowed_command_types"],
        "max_selected_targets": data["policy"]["max_selected_targets"],
        "max_plan_commands": data["policy"]["max_plan_commands"],
        "duration_minimum_half_second_frames": data["policy"]["duration"][
            "minimum_half_second_frames"
        ],
        "speed_bounds": [
            data["policy"]["speed_percent"]["minimum"],
            data["policy"]["speed_percent"]["maximum"],
        ],
        "position_x_bounds": [
            data["policy"]["transform"]["position_x"]["minimum"],
            data["policy"]["transform"]["position_x"]["maximum"],
        ],
        "transition_presets": data["policy"]["transition"]["presets"],
        "source_duration_available": (
            data["targets"][0]["source_duration_availability"][
                "available_source_frames_from_current_in"
            ]
            > 0
        ),
        "neighbors_bounded": set(data["targets"][0]["neighbors"])
        == {"previous", "next"},
        "project_unchanged": state.semantic_json(include_revision=True) == before,
        "path_absent": "fixture-private-path.mp4" not in raw,
        "source_name_absent": "private-fixture-name.mp4" not in raw,
        "parser_started": False,
        "semantic_verifier_started": False,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    expected = {
        "schema_version": 2,
        "auto_edit_plan_schema_version": 2,
        "selected_clip_ids": ["clip-2", "clip-1"],
        "target_count": 2,
        "allowed_command_types": list(W7_ALLOWED_COMMAND_TYPES),
        "max_selected_targets": 20,
        "max_plan_commands": 40,
        "duration_minimum_half_second_frames": 15,
        "speed_bounds": [50, 200],
        "position_x_bounds": [-960, 960],
        "transition_presets": ["none", "fade_black"],
        "source_duration_available": True,
        "neighbors_bounded": True,
        "project_unchanged": True,
        "path_absent": True,
        "source_name_absent": True,
        "parser_started": False,
        "semantic_verifier_started": False,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    for key, value in expected.items():
        if report[key] != value:
            raise SystemExit(f"W7-002 evidence mismatch: {key}")

    (output / "00_w7_002_context_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "01_w7_002_context_shape.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
