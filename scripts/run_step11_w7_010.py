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
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    L2AIProviderRequest,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.ai_l2_context import L2ContextBuilder
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
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
                    "schema_version": 2,
                    "base_project_revision": request.base_project_revision,
                    "request_id": request.request_id,
                    "summary": "Final integrated W7 mixed real-media closure.",
                    "commands": [
                        {
                            "command_type": "set_clip_effects",
                            "target_clip_id": "C001",
                            "enter_effect": "Rise",
                            "exit_effect": "Fade",
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
                            "position_x": 180,
                            "position_y": -90,
                            "scale_percent": 125,
                            "rotation_tenths": 100,
                            "opacity_percent": 80,
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
            ),
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write(path: Path, data: object) -> None:
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
    raise RuntimeError("W7-010 deterministic L2 job timed out")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    source_before = _sha256(video)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project(
        "ANG-S11-W7-010",
        "W7 Final Real Media Closure",
    )
    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 240:
        raise RuntimeError("W7-010 fixture requires at least 240 frames")

    session.execute(
        CommandBatch(
            "W7-010-SETUP",
            "Add final W7 closure clips",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        asset_id,
                        FrameTime(0, session.state.fps),
                        FrameTime(0, session.state.fps),
                        FrameTime(120, session.state.fps),
                    )
                ),
                AddClipCommand(
                    Clip(
                        "C002",
                        asset_id,
                        FrameTime(120, session.state.fps),
                        FrameTime(120, session.state.fps),
                        FrameTime(240, session.state.fps),
                    )
                ),
            ),
        )
    )

    baseline_hash = session.state.semantic_hash()
    baseline_revision = session.state.revision
    baseline_json = session.state.semantic_json(include_revision=True)
    baseline_preview = evidence / "preview_baseline.png"
    engine.preview_frame(session.state, 15, baseline_preview)

    scope = W7SelectedScope(("C001", "C002"))
    context_json = L2ContextBuilder().build(session.state, scope)
    request = L2AIProviderRequest(
        request_id="REQ-W7-010-REAL",
        base_project_revision=session.state.revision,
        instruction="Apply the final bounded mixed L2 real-media plan.",
        context_json=context_json,
    )

    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-w7-010-evidence"),
        label="Deterministic Gemini",
    )
    pool = CredentialPoolService(slots, backend)

    with AIPlanJobService(ClosureProvider(), pool) as jobs:
        jobs.submit(
            request,
            session.state,
            scope.clip_ids,
            session_id="w7-010-real-media",
        )
        terminal = _wait(jobs, request.request_id)
        if terminal.state is not AIJobState.SUCCESS:
            raise RuntimeError("W7-010 integrated provider/verifier chain failed")

        approvals = AIPlanApprovalService(jobs, session.bus)
        staged = approvals.stage_from_job_l2(
            request.request_id,
            session_id="w7-010-real-media",
        )
        diff_texts = approvals.diff_texts(staged.approval_id)
        if staged.state is not AIApprovalState.PENDING or len(diff_texts) != 6:
            raise RuntimeError("W7-010 review staging proof failed")
        if session.state.semantic_json(include_revision=True) != baseline_json:
            raise RuntimeError("W7-010 staging mutated canonical project")

        approvals.approve(staged.approval_id)
        applied = approvals.apply(staged.approval_id)

    if applied.state is not AIApprovalState.APPLIED:
        raise RuntimeError("W7-010 L2 plan was not atomically applied")
    if session.state.revision != baseline_revision + 1:
        raise RuntimeError("W7-010 apply did not increment revision exactly once")
    if session.state.timeline_end_frame != 210:
        raise RuntimeError("W7-010 mixed pacing result is not 210 frames")

    clip1 = session.state.clip("C001")
    clip2 = session.state.clip("C002")
    if clip1.properties.effects.enter_effect != "Rise":
        raise RuntimeError("W7-010 L1 effect did not reach canonical state")
    if clip1.duration_frames != 150:
        raise RuntimeError("W7-010 duration did not reach canonical state")
    if clip1.properties.video.scale_x_percent != 125:
        raise RuntimeError("W7-010 transform did not reach canonical state")
    if clip1.properties.transition.preset != "fade_black":
        raise RuntimeError("W7-010 C001 transition did not reach canonical state")
    if clip2.duration_frames != 60 or clip2.properties.speed.rate_percent != 200:
        raise RuntimeError("W7-010 speed did not reach canonical state")
    if clip2.properties.transition.duration_frames != 30:
        raise RuntimeError("W7-010 C002 transition did not reach canonical state")

    applied_hash = session.state.semantic_hash()
    applied_preview = evidence / "preview_ai_applied.png"
    engine.preview_frame(session.state, 15, applied_preview)
    if _sha256(baseline_preview) == _sha256(applied_preview):
        raise RuntimeError("W7-010 real preview did not change after L2 apply")

    export_path = evidence / "w7_010_mixed_export.mp4"
    engine.export(session.state, export_path)
    export_probe = probe.probe(export_path)
    if abs(export_probe.duration_frames - 210) > 3:
        raise RuntimeError("W7-010 real export timing mismatch")
    if not export_probe.has_audio:
        raise RuntimeError("W7-010 real export lost audio")

    project_path = evidence / "w7_010_applied.angproj"
    session.save(project_path)
    if session.dirty:
        raise RuntimeError("W7-010 project remained dirty after save")

    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    reopened_hash = reopened.state.semantic_hash()
    if reopened_hash != applied_hash:
        raise RuntimeError("W7-010 save/reopen semantic hash mismatch")
    if reopened.state.revision != session.state.revision:
        raise RuntimeError("W7-010 save/reopen revision mismatch")

    reopened_preview = evidence / "preview_reopened.png"
    engine.preview_frame(reopened.state, 15, reopened_preview)
    if _sha256(reopened_preview) != _sha256(applied_preview):
        raise RuntimeError("W7-010 reopened render differs from applied render")

    undo_state = session.undo()
    undo_hash = undo_state.semantic_hash()
    redo_state = session.redo()
    redo_hash = redo_state.semantic_hash()

    source_after = _sha256(video)
    report = {
        "status": "PASS",
        "provider_path": (
            "L2ContextBuilder -> AIPlanJobService -> AutoEditPlanVerifier -> "
            "AIPlanApprovalService -> CommandBatch(actor=ai)"
        ),
        "mixed_l1_l2_plan": True,
        "review_diff_count": len(diff_texts),
        "review_diffs_bounded": all(len(item) <= 280 and "→" in item for item in diff_texts),
        "canonical_unchanged_before_approval": baseline_json
        != ""
        and staged.base_project_revision == baseline_revision,
        "one_revision_apply": session.state.revision >= baseline_revision + 3,
        "applied_revision_recorded": applied.applied_revision == baseline_revision + 1,
        "real_pacing_timeline_frames": 210,
        "real_preview_changed": _sha256(baseline_preview) != _sha256(applied_preview),
        "real_export_frames": export_probe.duration_frames,
        "real_export_audio": export_probe.has_audio,
        "effect_applied": clip1.properties.effects.enter_effect == "Rise",
        "transform_applied": (
            clip1.properties.video.position_x == 180
            and clip1.properties.video.position_y == -90
            and clip1.properties.video.scale_x_percent == 125
            and clip1.properties.video.rotation_tenths == 100
            and clip1.properties.video.opacity_percent == 80
        ),
        "fade_black_applied": (
            clip1.properties.transition.preset == "fade_black"
            and clip2.properties.transition.preset == "fade_black"
        ),
        "save_reopen_hash_exact": reopened_hash == applied_hash,
        "save_reopen_render_exact": _sha256(reopened_preview) == _sha256(applied_preview),
        "undo_exact": undo_hash == baseline_hash,
        "redo_exact": redo_hash == applied_hash,
        "source_media_unchanged": source_before == source_after,
        "live_gemini_network_claimed": False,
        "later_wave_started": False,
    }

    required_true = (
        "mixed_l1_l2_plan",
        "review_diffs_bounded",
        "canonical_unchanged_before_approval",
        "applied_revision_recorded",
        "real_preview_changed",
        "real_export_audio",
        "effect_applied",
        "transform_applied",
        "fade_black_applied",
        "save_reopen_hash_exact",
        "save_reopen_render_exact",
        "undo_exact",
        "redo_exact",
        "source_media_unchanged",
    )
    if report["review_diff_count"] != 6:
        raise RuntimeError("W7-010 final diff count mismatch")
    if abs(int(report["real_export_frames"]) - 210) > 3:
        raise RuntimeError("W7-010 final export timing gate failed")
    if any(report[key] is not True for key in required_true):
        raise RuntimeError("W7-010 final real-media closure gate failed")
    if report["live_gemini_network_claimed"] is not False:
        raise RuntimeError("W7-010 cannot claim unexecuted live Gemini network proof")
    if report["later_wave_started"] is not False:
        raise RuntimeError("W7-010 crossed the W7 closure boundary")

    _write(evidence / "00_w7_010_report.json", report)
    _write(
        evidence / "01_review_and_apply.json",
        {
            "approval_id": staged.approval_id,
            "batch_id": applied.batch_id,
            "diffs": diff_texts,
            "base_revision": baseline_revision,
            "applied_revision": applied.applied_revision,
            "applied_semantic_hash": applied_hash,
        },
    )
    _write(
        evidence / "02_real_media.json",
        {
            "baseline_preview_sha256": _sha256(baseline_preview),
            "applied_preview_sha256": _sha256(applied_preview),
            "reopened_preview_sha256": _sha256(reopened_preview),
            "export_sha256": _sha256(export_path),
            "export_frames": export_probe.duration_frames,
            "export_audio": export_probe.has_audio,
            "source_before_sha256": source_before,
            "source_after_sha256": source_after,
        },
    )
    _write(
        evidence / "03_persistence_undo_redo.json",
        {
            "project_file_sha256": _sha256(project_path),
            "saved_semantic_hash": applied_hash,
            "reopened_semantic_hash": reopened_hash,
            "undo_semantic_hash": undo_hash,
            "baseline_semantic_hash": baseline_hash,
            "redo_semantic_hash": redo_hash,
        },
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
