from __future__ import annotations

import json
import threading
import time
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    ProviderContractError,
    ProviderErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectState,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class EvidenceProvider:
    def __init__(self, response_json: str) -> None:
        self.response_json = response_json
        self.thread_ids: list[int] = []
        self.calls = 0

    def request_plan(self, request, credential, cancellation=None):
        del credential
        self.calls += 1
        self.thread_ids.append(threading.get_ident())
        if cancellation is not None and cancellation.cancelled:
            raise RuntimeError("unexpected cancellation")
        return ProviderPlanResponse(request.request_id, self.response_json)


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-evidence",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "b" * 64,
    )
    clip = Clip(
        "clip-evidence",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(120, fps),
    )
    state = replace(
        ProjectState.create("project-evidence", "W6-007 evidence", fps),
        revision=21,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(clip,)),),
    )
    state.validate()
    return state


def _payload() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": 21,
            "request_id": "REQ-EVIDENCE-007",
            "summary": "Apply one qualified entrance effect.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-evidence",
                    "enter_effect": "Rise",
                    "intensity_percent": 115,
                }
            ],
        }
    )


def _wait(service: AIPlanJobService):
    for _ in range(300):
        snapshot = service.snapshot("REQ-EVIDENCE-007")
        if snapshot.state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            return snapshot
        time.sleep(0.01)
    raise RuntimeError("evidence job timed out")


def main() -> int:
    evidence = Path("artifacts/step11/w6-007/evidence")
    evidence.mkdir(parents=True, exist_ok=True)

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-evidence-value"),
        label="Evidence Gemini",
    )
    pool = CredentialPoolService(slots, backend)
    provider = EvidenceProvider(_payload())
    state = _state()
    before = state.semantic_json(include_revision=True)
    caller_thread = threading.get_ident()
    request = AIProviderRequest(
        "REQ-EVIDENCE-007",
        21,
        "Add subtle L1 motion.",
        '{"selected_targets":[{"clip_id":"clip-evidence"}]}',
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(request, state, ("clip-evidence",), session_id="evidence-session")
        terminal = _wait(service)
        verified = service.take_verified(
            "REQ-EVIDENCE-007",
            state,
            session_id="evidence-session",
        )

    report = {
        "status": "PASS",
        "provider_off_caller_thread": bool(provider.thread_ids)
        and provider.thread_ids[0] != caller_thread,
        "job_state": terminal.state.value,
        "provider_calls": provider.calls,
        "verified_command_count": verified.command_count,
        "candidate_revision": verified.candidate_revision,
        "canonical_state_unchanged": state.semantic_json(include_revision=True) == before,
        "credential_not_in_snapshot": "runtime-evidence-value" not in repr(terminal),
        "gemini_network_used_in_deterministic_evidence": False,
        "approval_apply_started": False,
        "w6_ui_started": False,
    }
    if not all(
        (
            report["status"] == "PASS",
            report["provider_off_caller_thread"] is True,
            report["job_state"] == "SUCCESS",
            report["provider_calls"] == 1,
            report["verified_command_count"] == 1,
            report["candidate_revision"] == 21,
            report["canonical_state_unchanged"] is True,
            report["credential_not_in_snapshot"] is True,
            report["gemini_network_used_in_deterministic_evidence"] is False,
            report["approval_apply_started"] is False,
            report["w6_ui_started"] is False,
        )
    ):
        raise SystemExit("W6-007 deterministic evidence failed")

    (evidence / "00_w6_007_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
