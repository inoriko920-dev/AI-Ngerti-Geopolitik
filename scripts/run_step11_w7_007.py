from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import EffectEditProposal
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import (
    AutoEditPlanVerifier,
    VerifiedAutoEditPlan,
)
from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import (
    Clip,
    FrameTime,
    ProjectState,
    TransitionProperties,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_creative import build_w4_creative_plan
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


def _apply_verified(
    state: ProjectState,
    verified: VerifiedAutoEditPlan,
) -> ProjectState:
    candidate = state
    for command in verified.translated_commands:
        candidate = command.apply(candidate)
        candidate.validate()
    if candidate.semantic_hash() != verified.candidate_semantic_hash:
        raise AssertionError("translated candidate diverged from verifier proof")
    return candidate


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
        "ANG-S11-W7-007",
        "W7 Transition Mixed Qualification",
    )
    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 240:
        raise AssertionError("W7-007 fixture requires at least 240 frames")

    session.execute(
        CommandBatch(
            batch_id="W7-007-SETUP",
            label="Add transition mixed qualification clips",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(
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
    baseline = session.state
    baseline.validate()
    baseline_hash = baseline.semantic_hash()
    baseline_json = baseline.semantic_json(include_revision=True)
    bus = CommandBus(baseline)
    verifier = AutoEditPlanVerifier()
    scope = W7SelectedScope(("C001", "C002"))

    transition_plan = AutoEditPlan(
        2,
        baseline.revision,
        "REQ-W7-007-TRANSITION",
        "Real fade-through-black transition qualification.",
        (TransitionEditProposal("C001", "fade_black", 30),),
    )
    transition_verified = verifier.verify(
        transition_plan,
        baseline,
        W7SelectedScope(("C001",)),
    )
    transition_command = transition_verified.translated_commands[0]
    if not isinstance(transition_command, SetClipPropertiesCommand):
        raise AssertionError("transition did not use SetClipPropertiesCommand")
    transition_candidate = _apply_verified(baseline, transition_verified)
    transition_state = transition_candidate.clip("C001").properties.transition
    if transition_state != TransitionProperties("fade_black", 30):
        raise AssertionError("transition candidate state mismatch")

    transition_base = build_w3_filter_plan(
        transition_candidate.clip("C001"),
        transition_candidate.fps,
    )
    transition_render_plan = build_w4_creative_plan(
        transition_candidate.clip("C001"),
        transition_candidate.fps,
        base_x=transition_base.overlay_x,
        base_y=transition_base.overlay_y,
    )
    transition_fades = tuple(
        item
        for item in transition_render_plan.post_filters
        if item.startswith("fade=t=")
    )
    if len(transition_fades) != 2 or not all(
        "color=black" in item for item in transition_fades
    ):
        raise AssertionError("fade_black did not map to two black fade filters")

    baseline_preview = evidence / "preview_transition_baseline_frame1.png"
    transition_preview = evidence / "preview_transition_fade_black_frame1.png"
    engine.preview_frame(baseline, 1, baseline_preview)
    engine.preview_frame(transition_candidate, 1, transition_preview)
    baseline_preview_hash = _sha256(baseline_preview)
    transition_preview_hash = _sha256(transition_preview)
    if baseline_preview_hash == transition_preview_hash:
        raise AssertionError("fade_black real preview did not differ from baseline")

    transition_export = evidence / "transition_fade_black_export.mp4"
    engine.export(transition_candidate, transition_export)
    transition_probe = probe.probe(transition_export)
    if abs(transition_probe.duration_frames - 240) > 3:
        raise AssertionError("transition export timing mismatch")
    if not transition_probe.has_audio:
        raise AssertionError("transition export lost audio")

    clear_verified = verifier.verify(
        AutoEditPlan(
            2,
            transition_candidate.revision,
            "REQ-W7-007-NONE",
            "Clear fade-through-black transition.",
            (TransitionEditProposal("C001", "none", 0),),
        ),
        transition_candidate,
        W7SelectedScope(("C001",)),
    )
    cleared_candidate = _apply_verified(transition_candidate, clear_verified)
    if cleared_candidate.clip("C001").properties.transition != TransitionProperties():
        raise AssertionError("none transition did not clear fade_black")

    mixed_plan = AutoEditPlan(
        2,
        baseline.revision,
        "REQ-W7-007-MIXED",
        "Mixed L1/L2 real-media qualification.",
        (
            EffectEditProposal(
                "C001",
                enter_effect="Rise",
                exit_effect="Fade",
                intensity_percent=110,
            ),
            DurationEditProposal("C001", 150),
            TransformEditProposal(
                "C001",
                position_x=180,
                position_y=-90,
                scale_percent=125,
                rotation_tenths=100,
                opacity_percent=80,
            ),
            TransitionEditProposal("C001", "fade_black", 45),
            SpeedEditProposal("C002", 200),
            TransitionEditProposal("C002", "fade_black", 30),
        ),
    )
    mixed_verified = verifier.verify(mixed_plan, baseline, scope)
    mixed_candidate = _apply_verified(baseline, mixed_verified)
    clip1 = mixed_candidate.clip("C001")
    clip2 = mixed_candidate.clip("C002")

    expected_types = (
        "SetClipPropertiesCommand",
        "SetClipDurationCommand",
        "SetClipPropertiesCommand",
        "SetClipPropertiesCommand",
        "SetClipSpeedCommand",
        "SetClipPropertiesCommand",
    )
    if mixed_verified.translated_command_types != expected_types:
        raise AssertionError(
            "mixed plan did not reuse expected canonical manual owners"
        )
    if mixed_candidate.timeline_end_frame != 210:
        raise AssertionError("mixed plan sequential pacing result mismatch")
    if clip1.properties.transition != TransitionProperties("fade_black", 45):
        raise AssertionError("mixed plan C001 transition mismatch")
    if clip2.duration_frames != 60:
        raise AssertionError("mixed plan C002 speed duration mismatch")
    if clip2.properties.transition != TransitionProperties("fade_black", 30):
        raise AssertionError("mixed plan C002 transition mismatch")

    mixed_preview = evidence / "preview_mixed_frame15.png"
    engine.preview_frame(mixed_candidate, 15, mixed_preview)

    mixed_export = evidence / "mixed_plan_export.mp4"
    engine.export(mixed_candidate, mixed_export)
    mixed_probe = probe.probe(mixed_export)
    if abs(mixed_probe.duration_frames - 210) > 3:
        raise AssertionError("mixed plan export timing mismatch")
    if not mixed_probe.has_audio:
        raise AssertionError("mixed plan export lost audio")

    if baseline.semantic_json(include_revision=True) != baseline_json:
        raise AssertionError("W7-007 qualification mutated canonical baseline")
    if baseline.semantic_hash() != baseline_hash:
        raise AssertionError("W7-007 baseline semantic hash changed")
    if bus.can_undo or bus.can_redo:
        raise AssertionError("W7-007 qualification created CommandBus history")

    source_after = _sha256(video)
    if source_before != source_after:
        raise AssertionError("W7-007 qualification changed source media")

    transition_detail = {
        "request_id": transition_verified.plan.request_id,
        "translated_command": type(transition_command).__name__,
        "candidate_hash_matches_verifier": (
            transition_candidate.semantic_hash()
            == transition_verified.candidate_semantic_hash
        ),
        "preset": transition_state.preset,
        "duration_frames": transition_state.duration_frames,
        "post_filters": list(transition_render_plan.post_filters),
        "real_preview_baseline_sha256": baseline_preview_hash,
        "real_preview_transition_sha256": transition_preview_hash,
        "real_preview_changed": baseline_preview_hash != transition_preview_hash,
        "real_export_sha256": _sha256(transition_export),
        "real_export_frames": transition_probe.duration_frames,
        "real_export_audio": transition_probe.has_audio,
        "none_clear_verified": (
            cleared_candidate.clip("C001").properties.transition
            == TransitionProperties()
        ),
    }
    _write(evidence / "01_transition_qualification.json", transition_detail)

    mixed_detail = {
        "request_id": mixed_verified.plan.request_id,
        "command_count": mixed_verified.command_count,
        "target_count": mixed_verified.target_count,
        "selected_scope_count": mixed_verified.selected_scope_count,
        "translated_command_types": list(mixed_verified.translated_command_types),
        "candidate_hash_matches_verifier": (
            mixed_candidate.semantic_hash() == mixed_verified.candidate_semantic_hash
        ),
        "candidate_revision_unchanged": mixed_candidate.revision == baseline.revision,
        "timeline_end_frames": mixed_candidate.timeline_end_frame,
        "clip_1": {
            "duration_frames": clip1.duration_frames,
            "enter_effect": clip1.properties.effects.enter_effect,
            "exit_effect": clip1.properties.effects.exit_effect,
            "intensity_percent": clip1.properties.effects.intensity_percent,
            "position_x": clip1.properties.video.position_x,
            "position_y": clip1.properties.video.position_y,
            "scale_percent": clip1.properties.video.scale_x_percent,
            "rotation_tenths": clip1.properties.video.rotation_tenths,
            "opacity_percent": clip1.properties.video.opacity_percent,
            "transition_preset": clip1.properties.transition.preset,
            "transition_duration_frames": clip1.properties.transition.duration_frames,
        },
        "clip_2": {
            "timeline_start": clip2.timeline_start.frames,
            "duration_frames": clip2.duration_frames,
            "speed_percent": clip2.properties.speed.rate_percent,
            "transition_preset": clip2.properties.transition.preset,
            "transition_duration_frames": clip2.properties.transition.duration_frames,
        },
        "real_preview_sha256": _sha256(mixed_preview),
        "real_export_sha256": _sha256(mixed_export),
        "real_export_frames": mixed_probe.duration_frames,
        "real_export_audio": mixed_probe.has_audio,
    }
    _write(evidence / "02_mixed_plan_qualification.json", mixed_detail)

    report = {
        "status": "PASS",
        "transition_manual_owner_reused": isinstance(
            transition_command,
            SetClipPropertiesCommand,
        ),
        "transition_filter_fade_black": (
            len(transition_fades) == 2
            and all("color=black" in item for item in transition_fades)
        ),
        "transition_real_preview": baseline_preview_hash != transition_preview_hash,
        "transition_real_export": (
            transition_export.is_file() and transition_export.stat().st_size > 0
        ),
        "transition_export_audio": transition_probe.has_audio,
        "transition_none_clear": (
            cleared_candidate.clip("C001").properties.transition
            == TransitionProperties()
        ),
        "mixed_l1_l2_plan": (
            mixed_verified.command_count == 6
            and mixed_verified.target_count == 2
            and clip1.properties.effects.enter_effect == "Rise"
            and clip1.properties.transition.preset == "fade_black"
            and clip2.properties.speed.rate_percent == 200
        ),
        "mixed_candidate_hash_matches_verifier": (
            mixed_candidate.semantic_hash() == mixed_verified.candidate_semantic_hash
        ),
        "mixed_candidate_revision_unchanged": (
            mixed_candidate.revision == baseline.revision
        ),
        "mixed_real_export": mixed_export.is_file() and mixed_export.stat().st_size > 0,
        "mixed_export_audio": mixed_probe.has_audio,
        "mixed_export_frames": mixed_probe.duration_frames,
        "canonical_state_unchanged": baseline.semantic_hash() == baseline_hash,
        "command_bus_history_unchanged": not bus.can_undo and not bus.can_redo,
        "source_media_unchanged": source_before == source_after,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_ai_apply_started": False,
        "w7_008_provider_lifecycle_started": False,
    }

    for key in (
        "transition_manual_owner_reused",
        "transition_filter_fade_black",
        "transition_real_preview",
        "transition_real_export",
        "transition_export_audio",
        "transition_none_clear",
        "mixed_l1_l2_plan",
        "mixed_candidate_hash_matches_verifier",
        "mixed_candidate_revision_unchanged",
        "mixed_real_export",
        "mixed_export_audio",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
        "source_media_unchanged",
    ):
        if report[key] is not True:
            raise AssertionError(f"W7-007 evidence gate failed: {key}")

    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_008_provider_lifecycle_started",
    ):
        if report[key] is not False:
            raise AssertionError(f"W7-007 crossed later-task boundary: {key}")

    _write(evidence / "00_w7_007_transition_mixed_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
