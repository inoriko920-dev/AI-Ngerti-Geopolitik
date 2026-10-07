from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
    VideoProperties,
)


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-004-evidence",
        "fixture.mp4",
        "video",
        FrameTime(2400, fps),
        1920,
        1080,
        True,
        "8" * 64,
    )
    clips = tuple(
        Clip(
            f"clip-{index + 1}",
            asset.asset_id,
            FrameTime(index * 180, fps),
            FrameTime(index * 180, fps),
            FrameTime(index * 180 + 120, fps),
            properties=replace(
                ClipProperties(),
                video=VideoProperties(crop_left_percent=3),
                effects=EffectProperties("Fade", "Drift", 90, False),
            ),
        )
        for index in range(5)
    )
    state = replace(
        ProjectState.create("project-w7-004-evidence", "Verifier evidence", fps),
        revision=81,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload(commands: list[dict[str, object]], *, revision: int = 81) -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": revision,
            "request_id": "REQ-W7-004-EVIDENCE",
            "summary": "Sequential bounded L1/L2 verification evidence.",
            "commands": commands,
        }
    )


def _rejects(
    verifier: AutoEditPlanVerifier,
    raw: str,
    state: ProjectState,
    scope: W7SelectedScope,
    code: PlanErrorCode,
) -> bool:
    try:
        verifier.verify_payload(raw, state, scope)
    except PlanContractError as exc:
        return exc.code is code
    return False


def main() -> int:
    output = Path("artifacts/step11/w7-004/evidence")
    output.mkdir(parents=True, exist_ok=True)

    state = _state()
    before = state.semantic_json(include_revision=True)
    bus = CommandBus(state)
    scope = W7SelectedScope(("clip-1", "clip-2", "clip-3", "clip-4", "clip-5"))
    verifier = AutoEditPlanVerifier()
    commands = [
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
            "enter_effect": "Rise",
            "intensity_percent": 120,
        },
        {
            "command_type": "set_clip_duration",
            "target_clip_id": "clip-2",
            "duration_frames": 180,
        },
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-3",
            "rate_percent": 150,
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-4",
            "position_x": 100,
            "scale_percent": 110,
            "opacity_percent": 90,
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-5",
            "preset": "fade_black",
            "duration_frames": 12,
        },
    ]
    verified = verifier.verify_payload(_payload(commands), state, scope)

    stale = _payload(commands, revision=80)
    out_of_scope = _payload(
        [
            {
                "command_type": "set_clip_transform",
                "target_clip_id": "clip-5",
                "opacity_percent": 90,
            }
        ]
    )
    bad_duration = _payload(
        [
            {
                "command_type": "set_clip_duration",
                "target_clip_id": "clip-2",
                "duration_frames": 241,
            }
        ]
    )
    bad_position = _payload(
        [
            {
                "command_type": "set_clip_transform",
                "target_clip_id": "clip-1",
                "position_x": 961,
            }
        ]
    )
    sequential_transition = _payload(
        [
            {
                "command_type": "set_clip_speed",
                "target_clip_id": "clip-3",
                "rate_percent": 200,
            },
            {
                "command_type": "set_clip_transition",
                "target_clip_id": "clip-3",
                "preset": "fade_black",
                "duration_frames": 31,
            },
        ]
    )

    locked_state = replace(
        state,
        tracks=(replace(state.track("V1"), locked=True),),
    )
    locked_state.validate()

    report = {
        "status": "PASS",
        "schema_version": verified.plan.schema_version,
        "base_revision": verified.plan.base_project_revision,
        "candidate_revision": verified.candidate_revision,
        "candidate_hash_changed": verified.candidate_semantic_hash != state.semantic_hash(),
        "command_count": verified.command_count,
        "target_count": verified.target_count,
        "selected_scope_count": verified.selected_scope_count,
        "translated_command_types": list(verified.translated_command_types),
        "duration_ripple_application_owned": getattr(
            verified.translated_commands[1],
            "ripple",
            None,
        )
        is True,
        "speed_ripple_application_owned": getattr(
            verified.translated_commands[2],
            "ripple",
            None,
        )
        is True,
        "stale_rejected": _rejects(verifier, stale, state, scope, PlanErrorCode.STALE_PLAN),
        "out_of_scope_rejected": _rejects(
            verifier,
            out_of_scope,
            state,
            W7SelectedScope(("clip-1",)),
            PlanErrorCode.SEMANTIC_INVALID,
        ),
        "lock_rejected": _rejects(
            verifier,
            _payload(
                [
                    {
                        "command_type": "set_clip_transform",
                        "target_clip_id": "clip-1",
                        "opacity_percent": 90,
                    }
                ]
            ),
            locked_state,
            W7SelectedScope(("clip-1",)),
            PlanErrorCode.LOCK_CONFLICT,
        ),
        "duration_policy_rejected": _rejects(
            verifier,
            bad_duration,
            state,
            W7SelectedScope(("clip-2",)),
            PlanErrorCode.SEMANTIC_INVALID,
        ),
        "canvas_policy_rejected": _rejects(
            verifier,
            bad_position,
            state,
            W7SelectedScope(("clip-1",)),
            PlanErrorCode.SEMANTIC_INVALID,
        ),
        "sequential_transition_rejected": _rejects(
            verifier,
            sequential_transition,
            state,
            W7SelectedScope(("clip-3",)),
            PlanErrorCode.SEMANTIC_INVALID,
        ),
        "canonical_state_unchanged": state.semantic_json(include_revision=True) == before,
        "command_bus_history_unchanged": bus.can_undo is False and bus.can_redo is False,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
        "w7_005_pacing_qualification_started": False,
    }

    required_true = (
        "candidate_hash_changed",
        "duration_ripple_application_owned",
        "speed_ripple_application_owned",
        "stale_rejected",
        "out_of_scope_rejected",
        "lock_rejected",
        "duration_policy_rejected",
        "canvas_policy_rejected",
        "sequential_transition_rejected",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
    )
    for key in required_true:
        if report[key] is not True:
            raise SystemExit(f"W7-004 evidence failed: {key}")
    if report["schema_version"] != 2 or report["base_revision"] != 81:
        raise SystemExit("W7-004 evidence schema/base mismatch")
    if report["candidate_revision"] != 81:
        raise SystemExit("W7-004 dry run must not commit a revision")
    if report["command_count"] != 5 or report["target_count"] != 5:
        raise SystemExit("W7-004 evidence command/target mismatch")
    if report["selected_scope_count"] != 5:
        raise SystemExit("W7-004 evidence selected scope mismatch")
    if any(
        report[key] is not False
        for key in (
            "provider_profile_changed",
            "runtime_ui_changed",
            "canonical_apply_started",
            "w7_005_pacing_qualification_started",
        )
    ):
        raise SystemExit("W7-004 crossed a later-task boundary")

    (output / "00_w7_004_verifier_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
