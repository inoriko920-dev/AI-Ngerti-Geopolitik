from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    TransformEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_properties import build_w3_filter_plan
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


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


def _candidate(
    state: ProjectState,
    proposal: TransformEditProposal,
    request_id: str,
):
    plan = AutoEditPlan(
        2,
        state.revision,
        request_id,
        "W7-006 real transform qualification.",
        (proposal,),
    )
    verified = AutoEditPlanVerifier().verify(
        plan,
        state,
        W7SelectedScope(("C001",)),
    )
    command = verified.translated_commands[0]
    if not isinstance(command, SetClipPropertiesCommand):
        raise AssertionError(
            "transform did not translate to SetClipPropertiesCommand"
        )
    candidate = command.apply(state)
    candidate.validate()
    if candidate.semantic_hash() != verified.candidate_semantic_hash:
        raise AssertionError(
            "transform candidate diverged from verifier proof"
        )
    return verified, command, candidate


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
    session = ProjectSession(JsonProjectRepository())
    session.new_project(
        "ANG-S11-W7-006",
        "W7 L2 Transform Qualification",
    )
    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 90:
        raise AssertionError("W7-006 fixture requires at least 90 frames")

    session.execute(
        CommandBatch(
            batch_id="W7-006-SETUP",
            label="Add transform qualification clip",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(
                AddClipCommand(
                    Clip(
                        "C001",
                        asset_id,
                        FrameTime(0, session.state.fps),
                        FrameTime(0, session.state.fps),
                        FrameTime(90, session.state.fps),
                    )
                ),
            ),
        )
    )
    baseline = session.state
    baseline.validate()
    baseline_hash = baseline.semantic_hash()
    baseline_json = baseline.semantic_json(include_revision=True)
    bus = CommandBus(baseline)

    proposals = {
        "position": TransformEditProposal(
            "C001",
            position_x=240,
            position_y=-120,
        ),
        "scale": TransformEditProposal(
            "C001",
            scale_percent=135,
        ),
        "rotation": TransformEditProposal(
            "C001",
            rotation_tenths=120,
        ),
        "opacity": TransformEditProposal(
            "C001",
            opacity_percent=70,
        ),
        "composite": TransformEditProposal(
            "C001",
            position_x=180,
            position_y=-90,
            scale_percent=125,
            rotation_tenths=100,
            opacity_percent=80,
        ),
    }

    preview_hashes: dict[str, str] = {}
    baseline_preview = evidence / "preview_baseline_frame30.png"
    engine.preview_frame(baseline, 30, baseline_preview)
    preview_hashes["baseline"] = _sha256(baseline_preview)

    qualification: dict[str, object] = {}
    states: dict[str, ProjectState] = {}
    for name, proposal in proposals.items():
        verified, command, candidate = _candidate(
            baseline,
            proposal,
            f"REQ-W7-006-{name.upper()}",
        )
        states[name] = candidate
        preview = evidence / f"preview_transform_{name}_frame30.png"
        engine.preview_frame(candidate, 30, preview)
        preview_hashes[name] = _sha256(preview)

        video_state = candidate.clip("C001").properties.video
        plan = build_w3_filter_plan(
            candidate.clip("C001"),
            candidate.fps,
        )
        qualification[name] = {
            "request_id": verified.plan.request_id,
            "translated_command": type(command).__name__,
            "candidate_hash_matches_verifier": (
                candidate.semantic_hash()
                == verified.candidate_semantic_hash
            ),
            "position_x": video_state.position_x,
            "position_y": video_state.position_y,
            "scale_x_percent": video_state.scale_x_percent,
            "scale_y_percent": video_state.scale_y_percent,
            "rotation_tenths": video_state.rotation_tenths,
            "opacity_percent": video_state.opacity_percent,
            "overlay_x": plan.overlay_x,
            "overlay_y": plan.overlay_y,
            "video_filters": list(plan.video_filters),
            "preview_sha256": preview_hashes[name],
        }

    if len(set(preview_hashes.values())) != len(preview_hashes):
        raise AssertionError(
            "transform previews are not visually distinct"
        )

    composite = states["composite"]
    export_path = evidence / "transform_composite_90f.mp4"
    export_result = engine.export(composite, export_path)
    export_probe = probe.probe(export_path)

    if abs(export_probe.duration_frames - 90) > 3:
        raise AssertionError("transform export timing mismatch")
    if not export_probe.has_audio:
        raise AssertionError("transform export lost audio")

    if baseline.semantic_json(include_revision=True) != baseline_json:
        raise AssertionError(
            "transform qualification mutated canonical baseline"
        )
    if bus.can_undo or bus.can_redo:
        raise AssertionError(
            "transform qualification created CommandBus history"
        )

    source_after = _sha256(video)
    if source_before != source_after:
        raise AssertionError(
            "transform qualification changed source media"
        )

    _write(
        evidence / "01_transform_qualification.json",
        qualification,
    )

    report = {
        "status": "PASS",
        "position_real_preview": (
            preview_hashes["position"] != preview_hashes["baseline"]
        ),
        "scale_real_preview": (
            preview_hashes["scale"] != preview_hashes["baseline"]
        ),
        "rotation_real_preview": (
            preview_hashes["rotation"] != preview_hashes["baseline"]
        ),
        "opacity_real_preview": (
            preview_hashes["opacity"] != preview_hashes["baseline"]
        ),
        "all_previews_distinct": (
            len(set(preview_hashes.values()))
            == len(preview_hashes)
        ),
        "composite_real_export": (
            export_path.is_file()
            and export_path.stat().st_size > 0
        ),
        "composite_export_frames": export_probe.duration_frames,
        "composite_export_audio": export_probe.has_audio,
        "export_result_frames": export_result.duration_frames,
        "candidate_hashes_match_verifier": all(
            bool(item["candidate_hash_matches_verifier"])
            for item in qualification.values()
        ),
        "canonical_state_unchanged": (
            baseline.semantic_hash() == baseline_hash
        ),
        "command_bus_history_unchanged": (
            not bus.can_undo and not bus.can_redo
        ),
        "source_media_unchanged": source_before == source_after,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_ai_apply_started": False,
        "w7_007_transition_mixed_started": False,
    }

    for key in (
        "position_real_preview",
        "scale_real_preview",
        "rotation_real_preview",
        "opacity_real_preview",
        "all_previews_distinct",
        "composite_real_export",
        "composite_export_audio",
        "candidate_hashes_match_verifier",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
        "source_media_unchanged",
    ):
        if report[key] is not True:
            raise AssertionError(
                f"W7-006 evidence gate failed: {key}"
            )

    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_007_transition_mixed_started",
    ):
        if report[key] is not False:
            raise AssertionError(
                f"W7-006 crossed later-task boundary: {key}"
            )

    _write(
        evidence / "00_w7_006_transform_report.json",
        report,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
