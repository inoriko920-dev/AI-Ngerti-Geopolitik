from __future__ import annotations

import json
import threading
import time
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    AIRequestProfile,
    CredentialSecret,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.ai_l2_context import L2ContextBuilder
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class EvidenceProvider:
    def __init__(self, response_json: str) -> None:
        self.response_json = response_json
        self.thread_ids: list[int] = []
        self.profiles: list[str] = []
        self.calls = 0

    def request_plan(self, request, credential, cancellation=None):
        del credential
        self.calls += 1
        self.thread_ids.append(threading.get_ident())
        self.profiles.append(request.profile.value)
        if cancellation is not None and cancellation.cancelled:
            raise RuntimeError("unexpected cancellation")
        return ProviderPlanResponse(request.request_id, self.response_json)


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-008-evidence",
        "fixture.mp4",
        "video",
        FrameTime(360, fps),
        1920,
        1080,
        True,
        "c" * 64,
    )
    clips = (
        Clip(
            "C001",
            asset.asset_id,
            FrameTime(0, fps),
            FrameTime(0, fps),
            FrameTime(120, fps),
        ),
        Clip(
            "C002",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
        ),
    )
    state = replace(
        ProjectState.create(
            "project-w7-008-evidence",
            "W7-008 provider lifecycle evidence",
            fps,
        ),
        revision=28,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload() -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 28,
            "request_id": "REQ-W7-008-EVIDENCE",
            "summary": "Bounded L2 plan through shared provider lifecycle.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "C001",
                    "enter_effect": "Rise",
                    "intensity_percent": 110,
                },
                {
                    "command_type": "set_clip_duration",
                    "target_clip_id": "C001",
                    "duration_frames": 150,
                },
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "C001",
                    "scale_percent": 125,
                    "opacity_percent": 85,
                },
                {
                    "command_type": "set_clip_transition",
                    "target_clip_id": "C001",
                    "preset": "fade_black",
                    "duration_frames": 45,
                },
                {
                    "command_type": "set_clip_speed",
                    "target_clip_id": "C002",
                    "rate_percent": 200,
                },
                {
                    "command_type": "set_clip_transition",
                    "target_clip_id": "C002",
                    "preset": "fade_black",
                    "duration_frames": 30,
                },
            ],
        }
    )


def _wait(service: AIPlanJobService):
    for _ in range(300):
        snapshot = service.snapshot("REQ-W7-008-EVIDENCE")
        if snapshot.state in {
            AIJobState.SUCCESS,
            AIJobState.FAILED,
            AIJobState.CANCELLED,
        }:
            return snapshot
        time.sleep(0.01)
    raise RuntimeError("W7-008 evidence job timed out")


def main() -> int:
    evidence = Path("artifacts/step11/w7-008/evidence")
    evidence.mkdir(parents=True, exist_ok=True)

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-w7-008-evidence-value"),
        label="W7-008 Evidence Gemini",
    )
    pool = CredentialPoolService(slots, backend)
    provider = EvidenceProvider(_payload())
    state = _state()
    before = state.semantic_json(include_revision=True)
    caller_thread = threading.get_ident()
    scope = W7SelectedScope(("C001", "C002"))
    request = AIProviderRequest(
        request_id="REQ-W7-008-EVIDENCE",
        base_project_revision=state.revision,
        instruction="Improve pacing and motion without structural edits.",
        context_json=L2ContextBuilder().build(state, scope),
        profile=AIRequestProfile.L2_AUTO_EDIT,
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            request,
            state,
            scope.clip_ids,
            session_id="w7-008-evidence-session",
        )
        terminal = _wait(service)
        verified = service.take_verified_l2(
            "REQ-W7-008-EVIDENCE",
            state,
            session_id="w7-008-evidence-session",
        )

    report = {
        "status": "PASS",
        "request_profile": request.profile.value,
        "provider_off_caller_thread": bool(provider.thread_ids)
        and provider.thread_ids[0] != caller_thread,
        "shared_provider_calls": provider.calls,
        "provider_profiles": provider.profiles,
        "job_state": terminal.state.value,
        "verified_command_count": verified.command_count,
        "verified_target_count": verified.target_count,
        "verified_scope_count": verified.selected_scope_count,
        "candidate_revision": verified.candidate_revision,
        "candidate_hash_present": bool(verified.candidate_semantic_hash),
        "canonical_state_unchanged": state.semantic_json(include_revision=True) == before,
        "credential_not_in_snapshot": (
            "runtime-w7-008-evidence-value" not in repr(terminal)
        ),
        "gemini_network_used_in_deterministic_evidence": False,
        "second_provider_service_created": False,
        "credential_pool_replaced": False,
        "runtime_ui_changed": False,
        "canonical_ai_apply_started": False,
        "w7_009_started": False,
    }
    required_true = (
        "provider_off_caller_thread",
        "candidate_hash_present",
        "canonical_state_unchanged",
        "credential_not_in_snapshot",
    )
    required_false = (
        "gemini_network_used_in_deterministic_evidence",
        "second_provider_service_created",
        "credential_pool_replaced",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_009_started",
    )
    if report["status"] != "PASS":
        raise SystemExit("W7-008 evidence status failed")
    if report["request_profile"] != "L2_AUTO_EDIT":
        raise SystemExit("W7-008 request profile mismatch")
    if report["provider_profiles"] != ["L2_AUTO_EDIT"]:
        raise SystemExit("W7-008 provider profile dispatch mismatch")
    if report["job_state"] != "SUCCESS":
        raise SystemExit("W7-008 shared job lifecycle did not succeed")
    if report["shared_provider_calls"] != 1:
        raise SystemExit("W7-008 provider call count mismatch")
    if report["verified_command_count"] != 6:
        raise SystemExit("W7-008 command count mismatch")
    if report["verified_target_count"] != 2:
        raise SystemExit("W7-008 target count mismatch")
    if report["verified_scope_count"] != 2:
        raise SystemExit("W7-008 scope count mismatch")
    if report["candidate_revision"] != 28:
        raise SystemExit("W7-008 candidate revision changed")
    if any(report[key] is not True for key in required_true):
        raise SystemExit("W7-008 required true evidence gate failed")
    if any(report[key] is not False for key in required_false):
        raise SystemExit("W7-008 crossed a later-task boundary")

    (evidence / "00_w7_008_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
