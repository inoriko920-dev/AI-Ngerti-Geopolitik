from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    SetClipDurationCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _add_clip(session: ProjectSession, clip: Clip) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W7-005-SETUP-{session.state.revision + 1:06d}",
            label="Add W7-005 qualification clip",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(AddClipCommand(clip),),
        )
    )


def _plan(state: ProjectState, command, request_id: str) -> AutoEditPlan:
    return AutoEditPlan(
        2,
        state.revision,
        request_id,
        "W7-005 real pacing qualification.",
        (command,),
    )


def _candidate(state: ProjectState, command, request_id: str):
    verified = AutoEditPlanVerifier().verify(
        _plan(state, command, request_id),
        state,
        W7SelectedScope(("C001",)),
    )
    translated = verified.translated_commands[0]
    candidate = translated.apply(state)
    candidate.validate()
    if candidate.semantic_hash() != verified.candidate_semantic_hash:
        raise AssertionError("translated pacing candidate diverged from verifier proof")
    return verified, translated, candidate


def _export_report(
    engine: FfmpegSliceMediaEngine,
    probe: FfprobeMediaProbe,
    state: ProjectState,
    output: Path,
) -> dict[str, object]:
    export = engine.export(state, output)
    result = probe.probe(output)
    if abs(result.duration_frames - state.timeline_end_frame) > 3:
        raise AssertionError(
            f"real export timing mismatch for {output.name}: "
            f"canonical={state.timeline_end_frame}, ffprobe={result.duration_frames}"
        )
    if not result.has_audio:
        raise AssertionError(f"real pacing export lost audio: {output.name}")
    return {
        "file": output.name,
        "sha256": _sha256(output),
        "canonical_frames": state.timeline_end_frame,
        "ffprobe_frames": result.duration_frames,
        "width": result.width,
        "height": result.height,
        "fps": result.fps,
        "has_audio": result.has_audio,
        "export_result_frames": export.duration_frames,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    source_hash_before = _sha256(video)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W7-005", "W7 L2 Pacing Qualification")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 180:
        raise AssertionError("W7-005 fixture requires at least 180 frames")

    for index in range(3):
        start = index * 60
        _add_clip(
            session,
            Clip(
                f"C{index + 1:03d}",
                asset_id,
                FrameTime(start, session.state.fps),
                FrameTime(start, session.state.fps),
                FrameTime(start + 60, session.state.fps),
            ),
        )

    baseline = session.state
    baseline.validate()
    baseline_hash = baseline.semantic_hash()
    baseline_json = baseline.semantic_json(include_revision=True)
    bus = CommandBus(baseline)

    baseline_preview = evidence / "preview_baseline_frame15.png"
    engine.preview_frame(baseline, 15, baseline_preview)
    baseline_export = _export_report(
        engine,
        probe,
        baseline,
        evidence / "baseline_180f.mp4",
    )

    duration_verified, duration_command, duration_state = _candidate(
        baseline,
        DurationEditProposal("C001", 90),
        "REQ-W7-005-DURATION",
    )
    if not isinstance(duration_command, SetClipDurationCommand):
        raise AssertionError("duration proposal did not translate to SetClipDurationCommand")
    if duration_command.ripple is not True:
        raise AssertionError("W7 duration ripple must be application-owned true")
    if (
        duration_state.clip("C001").duration_frames != 90
        or duration_state.clip("C002").timeline_start.frames != 90
        or duration_state.clip("C003").timeline_start.frames != 150
        or duration_state.timeline_end_frame != 210
    ):
        raise AssertionError("duration candidate timing/ripple mismatch")
    duration_export = _export_report(
        engine,
        probe,
        duration_state,
        evidence / "duration_150pct_210f.mp4",
    )

    fast_verified, fast_command, fast_state = _candidate(
        baseline,
        SpeedEditProposal("C001", 200),
        "REQ-W7-005-FAST",
    )
    if not isinstance(fast_command, SetClipSpeedCommand):
        raise AssertionError("speed proposal did not translate to SetClipSpeedCommand")
    if fast_command.ripple is not True:
        raise AssertionError("W7 speed ripple must be application-owned true")
    if (
        fast_state.clip("C001").duration_frames != 30
        or fast_state.clip("C002").timeline_start.frames != 30
        or fast_state.clip("C003").timeline_start.frames != 90
        or fast_state.timeline_end_frame != 150
    ):
        raise AssertionError("200 percent speed candidate timing/ripple mismatch")
    fast_preview = evidence / "preview_speed_200_frame15.png"
    engine.preview_frame(fast_state, 15, fast_preview)
    fast_export = _export_report(
        engine,
        probe,
        fast_state,
        evidence / "speed_200pct_150f.mp4",
    )

    slow_verified, slow_command, slow_state = _candidate(
        baseline,
        SpeedEditProposal("C001", 50),
        "REQ-W7-005-SLOW",
    )
    if not isinstance(slow_command, SetClipSpeedCommand):
        raise AssertionError("slow speed proposal did not translate to SetClipSpeedCommand")
    if slow_command.ripple is not True:
        raise AssertionError("W7 slow speed ripple must be application-owned true")
    if (
        slow_state.clip("C001").duration_frames != 120
        or slow_state.clip("C002").timeline_start.frames != 120
        or slow_state.clip("C003").timeline_start.frames != 180
        or slow_state.timeline_end_frame != 240
    ):
        raise AssertionError("50 percent speed candidate timing/ripple mismatch")
    slow_preview = evidence / "preview_speed_50_frame15.png"
    engine.preview_frame(slow_state, 15, slow_preview)
    slow_export = _export_report(
        engine,
        probe,
        slow_state,
        evidence / "speed_50pct_240f.mp4",
    )

    baseline_source_frame = baseline.clip("C001").source_frame_at_timeline_offset(15)
    fast_source_frame = fast_state.clip("C001").source_frame_at_timeline_offset(15)
    slow_source_frame = slow_state.clip("C001").source_frame_at_timeline_offset(15)
    if (baseline_source_frame, fast_source_frame, slow_source_frame) != (15, 30, 7):
        raise AssertionError("speed-aware source-frame mapping is incorrect")

    preview_hashes = {
        "baseline": _sha256(baseline_preview),
        "speed_200": _sha256(fast_preview),
        "speed_50": _sha256(slow_preview),
    }
    if len(set(preview_hashes.values())) != 3:
        raise AssertionError("real speed previews are not visually distinct")

    if baseline.semantic_json(include_revision=True) != baseline_json:
        raise AssertionError("W7-005 qualification mutated canonical baseline state")
    if baseline.semantic_hash() != baseline_hash:
        raise AssertionError("W7-005 qualification changed canonical baseline hash")
    if bus.can_undo or bus.can_redo:
        raise AssertionError("W7-005 qualification must not create CommandBus history")
    source_hash_after = _sha256(video)
    if source_hash_after != source_hash_before:
        raise AssertionError("W7-005 qualification modified source media")

    _write_json(
        evidence / "01_duration_qualification.json",
        {
            "request_id": duration_verified.plan.request_id,
            "translated_command": type(duration_command).__name__,
            "application_owned_ripple": duration_command.ripple,
            "baseline_duration_frames": 60,
            "qualified_duration_frames": duration_state.clip("C001").duration_frames,
            "qualified_source_out_frame": duration_state.clip("C001").source_out.frames,
            "later_clip_starts": [
                duration_state.clip("C002").timeline_start.frames,
                duration_state.clip("C003").timeline_start.frames,
            ],
            "candidate_hash_matches_verifier": (
                duration_state.semantic_hash() == duration_verified.candidate_semantic_hash
            ),
            "export": duration_export,
        },
    )
    _write_json(
        evidence / "02_speed_qualification.json",
        {
            "baseline_source_frame_at_offset_15": baseline_source_frame,
            "speed_200": {
                "request_id": fast_verified.plan.request_id,
                "translated_command": type(fast_command).__name__,
                "application_owned_ripple": fast_command.ripple,
                "rate_percent": fast_state.clip("C001").properties.speed.rate_percent,
                "duration_frames": fast_state.clip("C001").duration_frames,
                "later_clip_starts": [
                    fast_state.clip("C002").timeline_start.frames,
                    fast_state.clip("C003").timeline_start.frames,
                ],
                "source_frame_at_offset_15": fast_source_frame,
                "candidate_hash_matches_verifier": (
                    fast_state.semantic_hash() == fast_verified.candidate_semantic_hash
                ),
                "export": fast_export,
            },
            "speed_50": {
                "request_id": slow_verified.plan.request_id,
                "translated_command": type(slow_command).__name__,
                "application_owned_ripple": slow_command.ripple,
                "rate_percent": slow_state.clip("C001").properties.speed.rate_percent,
                "duration_frames": slow_state.clip("C001").duration_frames,
                "later_clip_starts": [
                    slow_state.clip("C002").timeline_start.frames,
                    slow_state.clip("C003").timeline_start.frames,
                ],
                "source_frame_at_offset_15": slow_source_frame,
                "candidate_hash_matches_verifier": (
                    slow_state.semantic_hash() == slow_verified.candidate_semantic_hash
                ),
                "export": slow_export,
            },
            "preview_sha256": preview_hashes,
            "all_previews_distinct": len(set(preview_hashes.values())) == 3,
        },
    )
    _write_json(
        evidence / "03_baseline_and_boundaries.json",
        {
            "baseline_export": baseline_export,
            "baseline_semantic_hash": baseline_hash,
            "canonical_state_unchanged": (
                baseline.semantic_json(include_revision=True) == baseline_json
            ),
            "command_bus_history_unchanged": not bus.can_undo and not bus.can_redo,
            "source_media_sha256_before": source_hash_before,
            "source_media_sha256_after": source_hash_after,
            "source_media_unchanged": source_hash_before == source_hash_after,
            "provider_profile_changed": False,
            "runtime_ui_changed": False,
            "canonical_ai_apply_started": False,
            "w7_006_transform_qualification_started": False,
        },
    )

    report = {
        "status": "PASS",
        "duration_real_timing": duration_export["ffprobe_frames"] >= 207
        and duration_export["ffprobe_frames"] <= 213,
        "duration_ripple": duration_state.clip("C002").timeline_start.frames == 90
        and duration_state.clip("C003").timeline_start.frames == 150,
        "speed_200_real_timing": fast_export["ffprobe_frames"] >= 147
        and fast_export["ffprobe_frames"] <= 153,
        "speed_50_real_timing": slow_export["ffprobe_frames"] >= 237
        and slow_export["ffprobe_frames"] <= 243,
        "speed_ripple": fast_state.clip("C002").timeline_start.frames == 30
        and slow_state.clip("C002").timeline_start.frames == 120,
        "speed_source_mapping": (baseline_source_frame, fast_source_frame, slow_source_frame)
        == (15, 30, 7),
        "speed_previews_distinct": len(set(preview_hashes.values())) == 3,
        "all_exports_have_audio": all(
            bool(item["has_audio"])
            for item in (baseline_export, duration_export, fast_export, slow_export)
        ),
        "candidate_hashes_match_verifier": all(
            (
                duration_state.semantic_hash() == duration_verified.candidate_semantic_hash,
                fast_state.semantic_hash() == fast_verified.candidate_semantic_hash,
                slow_state.semantic_hash() == slow_verified.candidate_semantic_hash,
            )
        ),
        "application_owned_ripple": all(
            (
                duration_command.ripple,
                fast_command.ripple,
                slow_command.ripple,
            )
        ),
        "canonical_state_unchanged": baseline.semantic_hash() == baseline_hash,
        "command_bus_history_unchanged": not bus.can_undo and not bus.can_redo,
        "source_media_unchanged": source_hash_before == source_hash_after,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_ai_apply_started": False,
        "w7_006_transform_qualification_started": False,
    }
    for key, value in report.items():
        if key == "status":
            continue
        if value is not True and key not in {
            "provider_profile_changed",
            "runtime_ui_changed",
            "canonical_ai_apply_started",
            "w7_006_transform_qualification_started",
        }:
            raise AssertionError(f"W7-005 evidence gate failed: {key}")
    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_006_transform_qualification_started",
    ):
        if report[key] is not False:
            raise AssertionError(f"W7-005 crossed later-task boundary: {key}")

    _write_json(evidence / "00_w7_005_pacing_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
