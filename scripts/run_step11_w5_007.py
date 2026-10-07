from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.microphone import MicrophoneRecordingService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_recorder import WindowsFfmpegRecorder
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    recorder = WindowsFfmpegRecorder()
    devices = recorder.devices()
    device_report = {
        "device_count": len(devices),
        "devices": [
            {"device_id": device.device_id, "name": device.name}
            for device in devices
        ],
    }
    _write_json(evidence / "01_microphone_devices.json", device_report)

    if not devices:
        report = {
            "status": "PASS_WITH_PROVISIONAL_MIC_HARDWARE",
            "real_device_available": False,
            "hardware_recording_attempted": False,
            "hardware_recording_bound": False,
            "fake_hardware_claimed": False,
            "reason": "GitHub Windows runner exposed no DirectShow audio input device",
        }
        _write_json(evidence / "00_w5_007_hardware_report.json", report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-007", "W5 Microphone Hardware")
    video_asset_id = MediaImportService(probe).import_path(session, video)
    video_asset = session.state.asset(video_asset_id)
    segment = min(180, video_asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-007-VIDEO",
            "Add W5-007 hardware video",
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

    recordings_dir = evidence / "recordings"
    output = MicrophoneRecordingService(recorder, probe).record_and_bind(
        session,
        recordings_dir,
        device_id=devices[0].device_id,
        max_duration_seconds=1.5,
        timeline_start_frame=0,
    )
    recorded = probe.probe(output)
    if recorded.media_type != "audio" or not recorded.has_audio:
        raise AssertionError("real microphone capture was not valid audio")
    if recorded.duration_seconds <= 0.05 or recorded.sample_rate <= 0:
        raise AssertionError("real microphone capture was empty/invalid")
    if session.state.narration is None:
        raise AssertionError("real microphone capture was not bound as narration")

    project_path = evidence / "w5_007_hardware.angproj"
    session.save(project_path)

    report = {
        "status": "PASS",
        "real_device_available": True,
        "hardware_recording_attempted": True,
        "hardware_recording_bound": True,
        "fake_hardware_claimed": False,
        "device_name": devices[0].name,
        "duration_seconds": recorded.duration_seconds,
        "sample_rate": recorded.sample_rate,
        "recorded_file": str(output),
    }
    _write_json(evidence / "00_w5_007_hardware_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
