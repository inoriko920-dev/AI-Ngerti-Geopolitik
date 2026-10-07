from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_approval import (
    AIApprovalState,
    AIPlanApprovalService,
)
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class EvidenceProvider:
    def request_plan(self, request, credential, cancellation=None):
        del credential, cancellation
        return ProviderPlanResponse(
            request.request_id,
            json.dumps(
                {
                    "schema_version": 1,
                    "base_project_revision": request.base_project_revision,
                    "request_id": request.request_id,
                    "summary": "Apply two qualified effects.",
                    "commands": [
                        {
                            "command_type": "set_clip_effects",
                            "target_clip_id": "clip-1",
                            "enter_effect": "Rise",
                        },
                        {
                            "command_type": "set_clip_effects",
                            "target_clip_id": "clip-2",
                            "exit_effect": "Tumble",
                            "intensity_percent": 110,
                        },
                    ],
                }
            ),
        )


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-evidence",
        "fixture.mp4",
        "video",
        FrameTime(600, fps),
        1920,
        1080,
        True,
        "e" * 64,
    )
    clips = (
        Clip(
            "clip-1",
            asset.asset_id,
            FrameTime(0, fps),
            FrameTime(0, fps),
            FrameTime(120, fps),
        ),
        Clip(
            "clip-2",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
        ),
    )
    state = replace(
        ProjectState.create("project-evidence-008", "W6-008 evidence", fps),
        revision=33,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _wait(jobs: AIPlanJobService) -> None:
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        snapshot = jobs.snapshot("REQ-EVIDENCE-008")
        if snapshot.state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            if snapshot.state is not AIJobState.SUCCESS:
                raise RuntimeError("evidence provider job failed")
            return
        time.sleep(0.01)
    raise RuntimeError("evidence provider job timed out")


def main() -> int:
    evidence = Path("artifacts/step11/w6-008/evidence")
    evidence.mkdir(parents=True, exist_ok=True)

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-evidence-value"),
        label="Evidence Gemini",
    )
    pool = CredentialPoolService(slots, backend)
    jobs = AIPlanJobService(EvidenceProvider(), pool)
    bus = CommandBus(_state())
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision

    try:
        jobs.submit(
            AIProviderRequest(
                "REQ-EVIDENCE-008",
                before_revision,
                "Use restrained L1 effects.",
                '{"selected_scope":{"clip_ids":["clip-1","clip-2"]}}',
            ),
            bus.state,
            ("clip-1", "clip-2"),
            session_id="evidence-session",
        )
        _wait(jobs)

        approvals = AIPlanApprovalService(jobs, bus)
        staged = approvals.stage_from_job(
            "REQ-EVIDENCE-008",
            session_id="evidence-session",
        )
        staged_hash = bus.state.semantic_hash()
        approved = approvals.approve(staged.approval_id)
        approved_hash = bus.state.semantic_hash()
        applied = approvals.apply(staged.approval_id)
        applied_hash = bus.state.semantic_hash()
        applied_revision = bus.state.revision

        undone = bus.undo()
        undo_hash = undone.semantic_hash()
        undo_is_single_transaction = not bus.can_undo and bus.can_redo
        redone = bus.redo()
        redo_hash = redone.semantic_hash()

        report = {
            "status": "PASS",
            "staged_state": staged.state.value,
            "approved_state": approved.state.value,
            "applied_state": applied.state.value,
            "stage_zero_mutation": staged_hash == before_hash,
            "approval_zero_mutation": approved_hash == before_hash,
            "one_revision_apply": applied_revision == before_revision + 1,
            "atomic_two_command_effect": (
                bus.state.clip("clip-1").properties.effects.enter_effect == "Rise"
                and bus.state.clip("clip-2").properties.effects.exit_effect == "Tumble"
            ),
            "undo_exact_before_semantics": undo_hash == before_hash,
            "undo_is_single_transaction": undo_is_single_transaction,
            "redo_exact_applied_semantics": redo_hash == applied_hash,
            "batch_id": applied.batch_id,
            "approval_apply_only": True,
            "w6_ui_started": False,
            "live_gemini_used": False,
        }
        expected = {
            "staged_state": AIApprovalState.PENDING.value,
            "approved_state": AIApprovalState.APPROVED.value,
            "applied_state": AIApprovalState.APPLIED.value,
            "batch_id": "AI-BATCH:REQ-EVIDENCE-008",
        }
        if report["status"] != "PASS":
            raise RuntimeError("W6-008 evidence status failed")
        for key in (
            "stage_zero_mutation",
            "approval_zero_mutation",
            "one_revision_apply",
            "atomic_two_command_effect",
            "undo_exact_before_semantics",
            "undo_is_single_transaction",
            "redo_exact_applied_semantics",
            "approval_apply_only",
        ):
            if report[key] is not True:
                raise RuntimeError(f"W6-008 evidence failed: {key}")
        if report["w6_ui_started"] is not False or report["live_gemini_used"] is not False:
            raise RuntimeError("W6-008 crossed a non-scope boundary")
        for key, value in expected.items():
            if report[key] != value:
                raise RuntimeError(f"W6-008 evidence mismatch: {key}")

        (evidence / "00_w6_008_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2, sort_keys=True))
    finally:
        jobs.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
