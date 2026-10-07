from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.microphone import (
    MicrophoneRecordingError,
    MicrophoneRecordingService,
)
from ai_ngerti_geopolitik.application.narration import NarrationImportService
from ai_ngerti_geopolitik.application.ports import (
    RecordingDevice,
    RecordingResult,
    SubtitleParseError,
)
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.application.subtitle_working_copy import (
    DirtySubtitleWorkingCopyError,
    SubtitleWorkingCopy,
)
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
    MediaToolError,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser


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


def _generate_narration(ffmpeg: str, path: Path) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000",
            "-t",
            "3",
            "-c:a",
            "pcm_s16le",
            str(path),
        ],
        check=True,
        shell=False,
    )


class FailingRecorder:
    def devices(self) -> tuple[RecordingDevice, ...]:
        return (RecordingDevice("MIC1", "Deterministic Failing Microphone"),)

    def capture(
        self,
        device_id: str,
        staging_path: Path,
        *,
        max_duration_seconds: float,
        cancellation=None,
    ) -> RecordingResult:
        del device_id, staging_path, max_duration_seconds, cancellation
        raise RuntimeError("deterministic capture failure")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    source_srt = evidence / "valid_source.srt"
    source_srt.write_text(
        "1\n00:00:01,000 --> 00:00:03,000\nClosure subtitle\n",
        encoding="utf-8",
        newline="\n",
    )
    source_srt_hash = _sha256(source_srt)

    malformed_srt = evidence / "malformed.srt"
    malformed_srt.write_text(
        "1\n00:00:01.000 --> 00:00:02,000\nMalformed\n",
        encoding="utf-8",
        newline="\n",
    )
    corrupt_audio = evidence / "corrupt_narration.wav"
    corrupt_audio.write_bytes(b"not-a-valid-wave-file")

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    narration_path = evidence / "valid_narration.wav"
    _generate_narration(engine.ffmpeg, narration_path)
    narration_source_hash = _sha256(narration_path)

    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-010", "W5 Closure")

    video_asset_id = MediaImportService(probe).import_path(session, video)
    video_asset = session.state.asset(video_asset_id)
    segment = min(180, video_asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-010-VIDEO",
            "Add closure video",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        video_asset_id,
                        FrameTime(0, session.state.fps),
                        FrameTime(0, session.state.fps),
                        FrameTime(segment, session.state.fps),
                    )
                ),
            ),
        )
    )
    video_hash = session.state.semantic_hash()

    SubtitleImportService(Utf8SrtParser()).import_path(session, source_srt)
    subtitle_hash = session.state.semantic_hash()
    narration_asset_id = NarrationImportService(probe).import_and_bind(
        session,
        narration_path,
        timeline_start_frame=60,
        gain_percent=80,
        fade_in_frames=15,
        fade_out_frames=15,
    )
    combined_hash = session.state.semantic_hash()

    session.undo()
    if session.state.semantic_hash() != subtitle_hash or session.state.narration is not None:
        raise AssertionError("narration Undo did not restore subtitle-only state")
    session.undo()
    if session.state.semantic_hash() != video_hash or session.state.subtitle is not None:
        raise AssertionError("subtitle Undo did not restore video-only state")
    session.redo()
    if session.state.semantic_hash() != subtitle_hash:
        raise AssertionError("subtitle Redo failed")
    session.redo()
    if session.state.semantic_hash() != combined_hash:
        raise AssertionError("narration Redo failed")

    if session.state.subtitle is None or session.state.narration is None:
        raise AssertionError("combined state missing after history walk")
    if session.state.narration.asset_id != narration_asset_id:
        raise AssertionError("narration asset identity changed after Redo")

    stable_hash = session.state.semantic_hash()

    malformed_error = ""
    try:
        SubtitleImportService(Utf8SrtParser()).import_path(session, malformed_srt)
    except SubtitleParseError as exc:
        malformed_error = str(exc)
    if not malformed_error:
        raise AssertionError("malformed SRT produced fake success")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("malformed SRT mutated project state")

    working = SubtitleWorkingCopy(session.state.subtitle)
    working.edit_selected(text="UNSAVED CLOSURE EDIT")
    dirty_error = ""
    try:
        working.reload(session.state.subtitle)
    except DirtySubtitleWorkingCopyError as exc:
        dirty_error = str(exc)
    if not dirty_error or not working.dirty:
        raise AssertionError("dirty working-copy guard failed")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("dirty working-copy guard mutated project state")

    narration_service = NarrationImportService(probe)
    missing_error = ""
    try:
        narration_service.import_and_bind(session, evidence / "missing_narration.wav")
    except MediaToolError as exc:
        missing_error = str(exc)
    if not missing_error:
        raise AssertionError("missing narration produced fake success")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("missing narration mutated project state")

    corrupt_error = ""
    try:
        narration_service.import_and_bind(session, corrupt_audio)
    except MediaToolError as exc:
        corrupt_error = str(exc)
    if not corrupt_error:
        raise AssertionError("corrupt narration produced fake success")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("corrupt narration mutated project state")

    held_narration = evidence / "valid_narration.held.wav"
    narration_path.replace(held_narration)
    missing_bound_error = ""
    preview_path = evidence / "should_not_exist_missing_narration.wav"
    try:
        engine.preview_narration_audio(
            session.state,
            timeline_frame=75,
            duration_frames=30,
            output_path=preview_path,
        )
    except MediaToolError as exc:
        missing_bound_error = str(exc)
    finally:
        held_narration.replace(narration_path)
    if not missing_bound_error:
        raise AssertionError("missing bound narration preview produced fake success")
    if preview_path.exists():
        raise AssertionError("missing bound narration left a fake preview output")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("missing bound narration mutated project state")

    recording_error = ""
    try:
        MicrophoneRecordingService(FailingRecorder(), probe).record_and_bind(
            session,
            evidence / "recording-failure",
            device_id="MIC1",
            max_duration_seconds=1.0,
        )
    except MicrophoneRecordingError as exc:
        recording_error = str(exc)
    if not recording_error:
        raise AssertionError("failed recording produced fake success")
    if session.state.semantic_hash() != stable_hash:
        raise AssertionError("failed recording replaced existing narration")
    if session.state.narration is None or session.state.narration.asset_id != narration_asset_id:
        raise AssertionError("failed recording clobbered existing narration")

    legacy_path = root / "tests" / "fixtures" / "step11_w4_pre_w5.angproj"
    legacy = repository.load(legacy_path)
    if legacy.subtitle is not None or legacy.narration is not None:
        raise AssertionError("pre-W5 W4 project did not load with safe W5 defaults")
    legacy_clip = legacy.clip("C001")
    if legacy_clip.properties.title.text != "GEOPOLITIK":
        raise AssertionError("pre-W5 title state was not preserved")
    if legacy_clip.properties.transition.preset != "fade_black":
        raise AssertionError("pre-W5 transition state was not preserved")
    if legacy_clip.properties.effects.enter_effect != "Rise":
        raise AssertionError("pre-W5 effect state was not preserved")

    if _sha256(source_srt) != source_srt_hash:
        raise AssertionError("closure changed source SRT")
    if _sha256(narration_path) != narration_source_hash:
        raise AssertionError("closure changed narration source")

    _write_json(
        evidence / "01_history.json",
        {
            "video_hash": video_hash,
            "subtitle_hash": subtitle_hash,
            "combined_hash": combined_hash,
            "undo_redo_restored": session.state.semantic_hash() == combined_hash,
            "subtitle_present": session.state.subtitle is not None,
            "narration_present": session.state.narration is not None,
        },
    )
    _write_json(
        evidence / "02_failure_paths.json",
        {
            "malformed_srt_rejected": bool(malformed_error),
            "malformed_srt_error": malformed_error,
            "dirty_reload_rejected": bool(dirty_error),
            "dirty_reload_error": dirty_error,
            "missing_narration_rejected": bool(missing_error),
            "missing_narration_error": missing_error,
            "corrupt_narration_rejected": bool(corrupt_error),
            "corrupt_narration_error": corrupt_error,
            "missing_bound_preview_rejected": bool(missing_bound_error),
            "missing_bound_preview_error": missing_bound_error,
            "fake_preview_created": preview_path.exists(),
            "failed_recording_rejected": bool(recording_error),
            "failed_recording_error": recording_error,
            "state_unchanged_after_failures": session.state.semantic_hash() == stable_hash,
        },
    )
    _write_json(
        evidence / "03_backward_compat.json",
        {
            "fixture": str(legacy_path),
            "subtitle_default_none": legacy.subtitle is None,
            "narration_default_none": legacy.narration is None,
            "title_preserved": legacy_clip.properties.title.text == "GEOPOLITIK",
            "transition_preserved": legacy_clip.properties.transition.preset == "fade_black",
            "effect_preserved": legacy_clip.properties.effects.enter_effect == "Rise",
        },
    )
    _write_json(
        evidence / "04_source_safety.json",
        {
            "source_srt_sha256": source_srt_hash,
            "source_srt_unchanged": _sha256(source_srt) == source_srt_hash,
            "narration_source_sha256": narration_source_hash,
            "narration_source_unchanged": _sha256(narration_path) == narration_source_hash,
            "existing_narration_preserved_after_recording_failure": (
                session.state.narration is not None
                and session.state.narration.asset_id == narration_asset_id
            ),
        },
    )

    report = {
        "status": "PASS_WITH_PROVISIONAL_MIC_HARDWARE",
        "subtitle_narration_undo_redo": session.state.semantic_hash() == combined_hash,
        "pre_w5_w4_safe_defaults": legacy.subtitle is None and legacy.narration is None,
        "malformed_srt_rejected_without_mutation": bool(malformed_error),
        "dirty_working_copy_guard": bool(dirty_error) and working.dirty,
        "missing_narration_rejected_without_mutation": bool(missing_error),
        "corrupt_narration_rejected_without_mutation": bool(corrupt_error),
        "missing_bound_narration_no_fake_preview": (
            bool(missing_bound_error) and not preview_path.exists()
        ),
        "failed_recording_preserves_existing_narration": (
            bool(recording_error)
            and session.state.narration is not None
            and session.state.narration.asset_id == narration_asset_id
        ),
        "source_srt_unchanged": _sha256(source_srt) == source_srt_hash,
        "narration_source_unchanged": _sha256(narration_path) == narration_source_hash,
        "microphone_hardware_qualifier": "PROVISIONAL",
        "fake_hardware_claimed": False,
        "asr_used": False,
        "speech_alignment_claimed": False,
    }
    _write_json(evidence / "00_w5_010_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
