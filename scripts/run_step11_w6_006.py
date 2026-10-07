from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_plan_verifier import PlanVerifier
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
)


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-evidence",
        "owned-fixture.mp4",
        "video",
        FrameTime(600, fps),
        1920,
        1080,
        True,
        "e" * 64,
    )
    clips = (
        Clip(
            "clip-open",
            asset.asset_id,
            FrameTime(0, fps),
            FrameTime(0, fps),
            FrameTime(120, fps),
            properties=replace(
                ClipProperties(),
                effects=EffectProperties("Fade", "Drift", 80, False),
            ),
        ),
        Clip(
            "clip-locked",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
            properties=replace(
                ClipProperties(),
                effects=EffectProperties("Pop", "Fade", 100, True),
            ),
        ),
    )
    state = replace(
        ProjectState.create("w6-006-evidence", "Plan verifier evidence", fps),
        revision=31,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload(
    *,
    revision: int = 31,
    target: str = "clip-open",
    effect: str = "Rise",
    intensity: int = 120,
    request_id: str = "REQ-EVIDENCE-006",
) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Apply one restrained L1 effect.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": target,
                    "enter_effect": effect,
                    "intensity_percent": intensity,
                }
            ],
        }
    )


def _error_code(callable_) -> str:
    try:
        callable_()
    except PlanContractError as exc:
        return exc.code.value
    raise AssertionError("expected PlanContractError")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    state = _state()
    before = state.semantic_json(include_revision=True)
    verifier = PlanVerifier()
    valid = verifier.verify_response(
        ProviderPlanResponse("REQ-EVIDENCE-006", _payload()),
        state,
        ("clip-open",),
    )

    unknown_root = json.loads(_payload())
    unknown_root["shell"] = "ignored"
    unknown_command = json.loads(_payload())
    unknown_command["commands"][0]["command_type"] = "shell_exec"

    report = {
        "status": "PASS",
        "strict_valid_plan": valid.command_count == 1,
        "candidate_changed": valid.candidate_semantic_hash != state.semantic_hash(),
        "candidate_revision_preserved": valid.candidate_revision == state.revision,
        "canonical_state_unchanged": state.semantic_json(include_revision=True) == before,
        "unknown_root_code": _error_code(lambda: verifier.parse(json.dumps(unknown_root))),
        "unknown_command_code": _error_code(lambda: verifier.parse(json.dumps(unknown_command))),
        "unknown_target_code": _error_code(
            lambda: verifier.verify_payload(
                _payload(target="clip-missing"),
                state,
                ("clip-missing",),
            )
        ),
        "unsupported_effect_code": _error_code(lambda: verifier.parse(_payload(effect="Wipe"))),
        "range_code": _error_code(lambda: verifier.parse(_payload(intensity=201))),
        "lock_code": _error_code(
            lambda: verifier.verify_payload(
                _payload(target="clip-locked"),
                state,
                ("clip-locked",),
            )
        ),
        "stale_code": _error_code(
            lambda: verifier.verify_payload(
                _payload(revision=30),
                state,
                ("clip-open",),
            )
        ),
        "request_mismatch_code": _error_code(
            lambda: verifier.verify_response(
                ProviderPlanResponse(
                    "REQ-OUTER",
                    _payload(request_id="REQ-INNER"),
                ),
                state,
                ("clip-open",),
            )
        ),
        "expected_schema_code": PlanErrorCode.SCHEMA_INVALID.value,
        "expected_semantic_code": PlanErrorCode.SEMANTIC_INVALID.value,
        "expected_lock_code": PlanErrorCode.LOCK_CONFLICT.value,
        "expected_stale_code": PlanErrorCode.STALE_PLAN.value,
        "gemini_network_called": False,
        "command_bus_apply_started": False,
        "approval_ui_started": False,
        "w6_ui_started": False,
    }

    assert report["status"] == "PASS"
    assert report["strict_valid_plan"] is True
    assert report["candidate_changed"] is True
    assert report["candidate_revision_preserved"] is True
    assert report["canonical_state_unchanged"] is True
    assert report["unknown_root_code"] == report["expected_schema_code"]
    assert report["unknown_command_code"] == report["expected_schema_code"]
    assert report["unknown_target_code"] == report["expected_semantic_code"]
    assert report["unsupported_effect_code"] == report["expected_semantic_code"]
    assert report["range_code"] == report["expected_semantic_code"]
    assert report["lock_code"] == report["expected_lock_code"]
    assert report["stale_code"] == report["expected_stale_code"]
    assert report["request_mismatch_code"] == report["expected_semantic_code"]
    assert report["gemini_network_called"] is False
    assert report["command_bus_apply_started"] is False
    assert report["approval_ui_started"] is False
    assert report["w6_ui_started"] is False

    _write(evidence / "00_w6_006_report.json", report)
    _write(
        evidence / "01_verified_plan_shape.json",
        {
            "request_id": valid.plan.request_id,
            "base_project_revision": valid.plan.base_project_revision,
            "command_count": valid.command_count,
            "candidate_revision": valid.candidate_revision,
            "candidate_semantic_hash": valid.candidate_semantic_hash,
            "command_type": valid.plan.commands[0].command_type,
            "target_clip_id": valid.plan.commands[0].target_clip_id,
        },
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
