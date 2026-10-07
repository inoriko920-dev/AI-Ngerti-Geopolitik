from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_approval import (
    AIApprovalState,
    AIPlanApprovalService,
)
from ai_ngerti_geopolitik.application.ai_context import L1ContextBuilder
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class ClosureProvider:
    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del credential, cancellation
        return ProviderPlanResponse(
            request.request_id,
            json.dumps(
                {
                    "schema_version": 1,
                    "base_project_revision": request.base_project_revision,
                    "request_id": request.request_id,
                    "summary": "Apply Rise as the qualified L1 entrance effect.",
                    "commands": [
                        {
                            "command_type": "set_clip_effects",
                            "target_clip_id": "C001",
                            "enter_effect": "Rise",
                            "intensity_percent": 120,
                        }
                    ],
                }
            ),
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _wait(service: AIPlanJobService, job_id: str) -> object:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        snapshot = service.snapshot(job_id)
        if snapshot.state in {
            AIJobState.SUCCESS,
            AIJobState.FAILED,
            AIJobState.CANCELLED,
        }:
            return snapshot
        time.sleep(0.01)
    raise RuntimeError("W6-010 deterministic AI job timed out")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    session = ProjectSession(JsonProjectRepository())
    session.new_project("ANG-S11-W6-010", "W6-010 AI Render Closure")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    segment = min(120, asset.duration.frames)
    if segment < 30:
        raise RuntimeError("W6-010 fixture is too short")

    session.execute(
        CommandBatch(
            "W6-010-ADD",
            "Add closure clip",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        asset_id,
                        FrameTime(0, session.state.fps),
                        FrameTime(0, session.state.fps),
                        FrameTime(segment, session.state.fps),
                    )
                ),
            ),
        )
    )

    before_hash = session.state.semantic_hash()
    before_revision = session.state.revision
    baseline = evidence / "preview_baseline.png"
    engine.preview_frame(session.state, 3, baseline)

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-closure-fixture"),
        label="Deterministic Gemini",
    )
    pool = CredentialPoolService(slots, backend)
    context = L1ContextBuilder().build(session.state, ("C001",))
    request = AIProviderRequest(
        "REQ-W6-010-RENDER",
        session.state.revision,
        "Set C001 enter effect to Rise and intensity_percent to 120.",
        context,
    )

    with AIPlanJobService(ClosureProvider(), pool) as jobs:
        jobs.submit(
            request,
            session.state,
            ("C001",),
            session_id="w6-010-render",
        )
        terminal = _wait(jobs, request.request_id)
        if terminal.state is not AIJobState.SUCCESS:
            raise RuntimeError("W6-010 deterministic provider chain failed")

        approvals = AIPlanApprovalService(jobs, session.bus)
        staged = approvals.stage_from_job(
            request.request_id,
            session_id="w6-010-render",
        )
        approvals.approve(staged.approval_id)
        applied = approvals.apply(staged.approval_id)

    if applied.state is not AIApprovalState.APPLIED:
        raise RuntimeError("W6-010 deterministic plan was not applied")

    edited = session.state.clip("C001")
    if edited.properties.effects.enter_effect != "Rise":
        raise RuntimeError("W6-010 AI-selected Rise effect was not canonical")
    if edited.properties.effects.intensity_percent != 120:
        raise RuntimeError("W6-010 AI-selected intensity was not canonical")

    applied_hash = session.state.semantic_hash()
    applied_revision = session.state.revision
    rendered = evidence / "preview_ai_applied.png"
    engine.preview_frame(session.state, 3, rendered)
    preview_changed = _sha256(baseline) != _sha256(rendered)
    if not preview_changed:
        raise RuntimeError("W6-010 AI-applied render is byte-identical to baseline")

    undo_state = session.undo()
    undo_hash = undo_state.semantic_hash()
    redo_state = session.redo()
    redo_hash = redo_state.semantic_hash()

    report = {
        "status": "PASS",
        "provider_path": "AIProviderPort -> PlanVerifier -> approval -> CommandBatch",
        "selected_effect": edited.properties.effects.enter_effect,
        "selected_intensity_percent": edited.properties.effects.intensity_percent,
        "render_effect_visible": preview_changed,
        "one_revision_apply": applied_revision == before_revision + 1,
        "undo_exact": undo_hash == before_hash,
        "redo_exact": redo_hash == applied_hash,
        "manual_editor_dependency": False,
        "live_gemini_used_in_deterministic_evidence": False,
    }
    if not all(
        (
            report["status"] == "PASS",
            report["selected_effect"] == "Rise",
            report["selected_intensity_percent"] == 120,
            report["render_effect_visible"] is True,
            report["one_revision_apply"] is True,
            report["undo_exact"] is True,
            report["redo_exact"] is True,
            report["manual_editor_dependency"] is False,
            report["live_gemini_used_in_deterministic_evidence"] is False,
        )
    ):
        raise RuntimeError("W6-010 deterministic closure gate failed")

    _write_json(evidence / "00_w6_010_report.json", report)
    _write_json(
        evidence / "01_render_proof.json",
        {
            "baseline_sha256": _sha256(baseline),
            "ai_applied_sha256": _sha256(rendered),
            "different": preview_changed,
            "effect": edited.properties.effects.enter_effect,
            "intensity_percent": edited.properties.effects.intensity_percent,
        },
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
