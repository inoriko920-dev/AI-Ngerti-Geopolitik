from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    SetNarrationTrackCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.narration import NarrationImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime, NarrationTrack
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


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _generate_narration(ffmpeg: str, output: Path) -> None:
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
            "4",
            "-c:a",
            "pcm_s16le",
            str(output),
        ],
        check=True,
        shell=False,
    )


def _mean_band_volume_db(
    ffmpeg: str,
    source: Path,
    *,
    start_seconds: float,
    duration_seconds: float,
) -> float:
    null_output = "NUL" if shutil.which("cmd") else "/dev/null"
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-ss",
            f"{start_seconds:.6f}",
            "-t",
            f"{duration_seconds:.6f}",
            "-i",
            str(source),
            "-af",
            "bandpass=f=440:width_type=h:w=80,volumedetect",
            "-f",
            "null",
            null_output,
        ],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"audio analysis failed: {result.stderr[-1200:]}")
    match = re.findall(r"mean_volume:\s*(-?inf|-?[0-9.]+) dB", result.stderr)
    if not match:
        raise AssertionError("mean_volume was not reported")
    value = match[-1]
    return -120.0 if value == "-inf" else float(value)


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
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-006", "W5 Narration")

    asset_id = MediaImportService(probe).import_path(session, video)
    video_asset = session.state.asset(asset_id)
    segment = min(180, video_asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-006-VIDEO",
            "Add W5-006 video",
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

    narration_path = evidence / "narration_440hz.wav"
    _generate_narration(engine.ffmpeg, narration_path)
    narration_source_hash = _sha256(narration_path)

    baseline_export = evidence / "export_baseline.mp4"
    engine.export(session.state, baseline_export)

    narration_asset_id = NarrationImportService(probe).import_and_bind(
        session,
        narration_path,
        timeline_start_frame=60,
        gain_percent=70,
        fade_in_frames=30,
        fade_out_frames=30,
    )
    if narration_asset_id != "A002" or session.state.narration is None:
        raise AssertionError("narration did not bind canonically")

    bound_hash = session.state.semantic_hash()
    preview_path = evidence / "narration_preview.wav"
    engine.preview_narration_audio(
        session.state,
        timeline_frame=75,
        duration_frames=30,
        output_path=preview_path,
    )
    preview_probe = probe.probe(preview_path)
    if preview_probe.media_type != "audio" or not preview_probe.has_audio:
        raise AssertionError("narration preview is not valid audio")
    preview_440 = _mean_band_volume_db(
        engine.ffmpeg,
        preview_path,
        start_seconds=0.0,
        duration_seconds=0.9,
    )
    if preview_440 < -35.0:
        raise AssertionError("narration is not audible in preview evidence")

    narrated_export = evidence / "export_narrated.mp4"
    engine.export(session.state, narrated_export)
    narrated_probe = probe.probe(narrated_export)
    if not narrated_probe.has_audio:
        raise AssertionError("narrated export lost audio")

    pre_offset_440 = _mean_band_volume_db(
        engine.ffmpeg,
        narrated_export,
        start_seconds=0.75,
        duration_seconds=0.5,
    )
    mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        narrated_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )
    baseline_mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        baseline_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )
    fade_start_440 = _mean_band_volume_db(
        engine.ffmpeg,
        narrated_export,
        start_seconds=2.05,
        duration_seconds=0.15,
    )

    if mid_440 < baseline_mid_440 + 8.0:
        raise AssertionError("narration spectral energy is not present in export")
    if mid_440 < pre_offset_440 + 8.0:
        raise AssertionError("narration offset is not reflected in export audio")
    if mid_440 < fade_start_440 + 4.0:
        raise AssertionError("narration fade-in is not reflected in export audio")

    current = session.state.narration
    if current is None:
        raise AssertionError("narration disappeared")
    muted = NarrationTrack(
        narration_id=current.narration_id,
        asset_id=current.asset_id,
        timeline_start=current.timeline_start,
        gain_percent=current.gain_percent,
        muted=True,
        fade_in_frames=current.fade_in_frames,
        fade_out_frames=current.fade_out_frames,
    )
    session.execute(
        CommandBatch(
            "W5-006-MUTE",
            "Mute narration",
            "manual",
            session.state.revision,
            (SetNarrationTrackCommand(muted),),
        )
    )
    muted_hash = session.state.semantic_hash()
    muted_export = evidence / "export_muted.mp4"
    engine.export(session.state, muted_export)
    muted_mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        muted_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )
    if mid_440 < muted_mid_440 + 8.0:
        raise AssertionError("narration mute is not reflected in export audio")

    session.undo()
    if session.state.semantic_hash() != bound_hash:
        raise AssertionError("narration mute Undo did not restore bound state")
    session.redo()
    if session.state.semantic_hash() != muted_hash:
        raise AssertionError("narration mute Redo did not restore muted state")
    session.undo()

    current = session.state.narration
    if current is None:
        raise AssertionError("narration disappeared after Undo")
    boosted = NarrationTrack(
        narration_id=current.narration_id,
        asset_id=current.asset_id,
        timeline_start=current.timeline_start,
        gain_percent=140,
        muted=False,
        fade_in_frames=current.fade_in_frames,
        fade_out_frames=current.fade_out_frames,
    )
    boosted_state = SetNarrationTrackCommand(boosted).apply(session.state)
    boosted_export = evidence / "export_boosted.mp4"
    engine.export(boosted_state, boosted_export)
    boosted_mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        boosted_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )
    expected_gain_db = 20.0 * math.log10(140 / 70)
    if boosted_mid_440 < mid_440 + expected_gain_db - 2.5:
        raise AssertionError("narration gain is not reflected in export audio")

    project_path = evidence / "w5_006_narration.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.semantic_hash() != session.state.semantic_hash():
        raise AssertionError("narration save/reopen changed canonical state")
    if reopened.state.narration != session.state.narration:
        raise AssertionError("narration binding/timing did not survive reopen")
    if _sha256(narration_path) != narration_source_hash:
        raise AssertionError("narration source was modified")

    _write_json(
        evidence / "01_binding.json",
        {
            "asset_id": narration_asset_id,
            "narration_id": session.state.narration.narration_id,
            "timeline_start_frame": session.state.narration.timeline_start.frames,
            "gain_percent": session.state.narration.gain_percent,
            "muted": session.state.narration.muted,
            "fade_in_frames": session.state.narration.fade_in_frames,
            "fade_out_frames": session.state.narration.fade_out_frames,
            "source_sha256": narration_source_hash,
            "source_unchanged": _sha256(narration_path) == narration_source_hash,
        },
    )
    _write_json(
        evidence / "02_audio_measurements.json",
        {
            "preview_440_mean_db": preview_440,
            "pre_offset_440_mean_db": pre_offset_440,
            "baseline_mid_440_mean_db": baseline_mid_440,
            "narrated_mid_440_mean_db": mid_440,
            "fade_start_440_mean_db": fade_start_440,
            "muted_mid_440_mean_db": muted_mid_440,
            "boosted_mid_440_mean_db": boosted_mid_440,
        },
    )
    _write_json(
        evidence / "03_history_persistence.json",
        {
            "bound_hash": bound_hash,
            "muted_hash": muted_hash,
            "undo_restored_bound": session.state.semantic_hash() == bound_hash,
            "save_reopen_hash_match": (
                reopened.state.semantic_hash() == session.state.semantic_hash()
            ),
        },
    )
    report = {
        "status": "PASS",
        "audio_import_bound": True,
        "frame_offset_proven": mid_440 >= pre_offset_440 + 8.0,
        "gain_proven": boosted_mid_440 >= mid_440 + expected_gain_db - 2.5,
        "mute_proven": mid_440 >= muted_mid_440 + 8.0,
        "fade_in_proven": mid_440 >= fade_start_440 + 4.0,
        "preview_audible": preview_440 >= -35.0,
        "export_audible": mid_440 >= baseline_mid_440 + 8.0,
        "export_has_audio": narrated_probe.has_audio,
        "undo_redo": True,
        "save_reopen": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "source_unchanged": _sha256(narration_path) == narration_source_hash,
        "microphone_started": False,
    }
    _write_json(evidence / "00_w5_006_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
