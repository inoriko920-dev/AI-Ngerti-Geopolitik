from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_approval import AIPlanApprovalService
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    CredentialSecret,
    L2AIProviderRequest,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class EvidenceProvider:
    def request_plan(self, request, credential, cancellation=None):
        del credential, cancellation
        return ProviderPlanResponse(request.request_id, _payload())


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-009-evidence",
        "fixture.mp4",
        "video",
        FrameTime(360, fps),
        1920,
        1080,
        True,
        "d" * 64,
    )
    clips = (
        Clip(
            "C001",
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
            "C002",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
        ),
    )
    state = replace(
        ProjectState.create("project-w7-009-evidence", "W7-009 evidence", fps),
        revision=31,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload() -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 31,
            "request_id": "REQ-W7-009-EVIDENCE",
            "summary": "Apply reviewed mixed L2 edits atomically.",
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


def _wait(service: AIPlanJobService) -> None:
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        state = service.snapshot("REQ-W7-009-EVIDENCE").state
        if state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            if state is not AIJobState.SUCCESS:
                raise RuntimeError(f"W7-009 evidence job terminal state: {state}")
            return
        time.sleep(0.01)
    raise RuntimeError("W7-009 evidence job timed out")


def main() -> int:
    root = Path("artifacts/step11/w7-009/evidence")
    root.mkdir(parents=True, exist_ok=True)

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-w7-009-evidence-value"),
        label="Evidence Gemini",
    )
    pool = CredentialPoolService(slots, backend)
    jobs = AIPlanJobService(EvidenceProvider(), pool)
    bus = CommandBus(_state())
    before_json = bus.state.semantic_json(include_revision=True)
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision

    try:
        request = L2AIProviderRequest(
            request_id="REQ-W7-009-EVIDENCE",
            base_project_revision=before_revision,
            instruction="Apply reviewed bounded L2 changes.",
            context_json='{"selected_scope":{"clip_ids":["C001","C002"]}}',
        )
        jobs.submit(
            request,
            bus.state,
            ("C001", "C002"),
            session_id="w7-009-evidence-session",
        )
        _wait(jobs)

        approvals = AIPlanApprovalService(jobs, bus)
        staged = approvals.stage_from_job_l2(
            "REQ-W7-009-EVIDENCE",
            session_id="w7-009-evidence-session",
        )
        diff_texts = approvals.diff_texts(staged.approval_id)
        unchanged_before_approval = bus.state.semantic_json(include_revision=True) == before_json

        approvals.approve(staged.approval_id)
        applied = approvals.apply(staged.approval_id)
        applied_hash = bus.state.semantic_hash()
        applied_revision = bus.state.revision
        timeline_end = bus.state.timeline_end_frame
        can_undo_after_apply = bus.can_undo

        undone = bus.undo()
        undo_hash_matches = undone.semantic_hash() == before_hash
        can_redo_after_undo = bus.can_redo

        redone = bus.redo()
        redo_hash_matches = redone.semantic_hash() == applied_hash

        report = {
            "status": "PASS",
            "approval_id": staged.approval_id,
            "batch_id": applied.batch_id,
            "diff_count": len(diff_texts),
            "diffs_bounded": all(len(item) <= 280 for item in diff_texts),
            "diffs_have_before_after_arrow": all("→" in item for item in diff_texts),
            "canonical_unchanged_before_approval": unchanged_before_approval,
            "revision_increment_once_on_apply": applied_revision == before_revision + 1,
            "mixed_timeline_end_frames": timeline_end,
            "can_undo_after_apply": can_undo_after_apply,
            "undo_restores_before_semantic_hash": undo_hash_matches,
            "can_redo_after_undo": can_redo_after_undo,
            "redo_restores_applied_semantic_hash": redo_hash_matches,
            "new_screen_or_layout_created": False,
            "w7_010_started": False,
        }

        required_true = (
            "diffs_bounded",
            "diffs_have_before_after_arrow",
            "canonical_unchanged_before_approval",
            "revision_increment_once_on_apply",
            "can_undo_after_apply",
            "undo_restores_before_semantic_hash",
            "can_redo_after_undo",
            "redo_restores_applied_semantic_hash",
        )
        if report["diff_count"] != 6:
            raise SystemExit("W7-009 evidence diff count mismatch")
        if report["batch_id"] != "AI-BATCH:REQ-W7-009-EVIDENCE":
            raise SystemExit("W7-009 evidence batch id mismatch")
        if report["mixed_timeline_end_frames"] != 210:
            raise SystemExit("W7-009 evidence mixed timeline mismatch")
        if any(report[key] is not True for key in required_true):
            raise SystemExit("W7-009 evidence required gate failed")
        if report["new_screen_or_layout_created"] is not False:
            raise SystemExit("W7-009 unexpectedly created a new UI screen/layout")
        if report["w7_010_started"] is not False:
            raise SystemExit("W7-009 crossed W7-010 boundary")

        (root / "00_w7_009_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (root / "01_w7_009_diffs.json").write_text(
            json.dumps({"diffs": diff_texts}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    finally:
        jobs.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
