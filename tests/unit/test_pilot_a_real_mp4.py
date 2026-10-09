"""Real native FFmpeg Pilot A: synthetic image-only H.264 MP4 on Windows."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.bootstrap.scene_cli import main as scene_cli
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.still_project_mp4 import (
    StillProjectMP4Error,
    export_still_project_mp4,
)
from ai_ngerti_geopolitik.application.scene_import_review import (
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.infrastructure.pilot_a_still_mp4 import (
    PilotAError,
    export_silent_h264_pilot_a,
    sha256_executable,
)
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import export_complete_still_sequence
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import plan_silent_h264_mp4

pytestmark = pytest.mark.skipif(
    os.environ.get("ANG_PILOT_A_FFMPEG") != "1",
    reason="Real external FFmpeg executes only in explicitly authorized Pilot A",
)


def _fixture(tmp_path: Path):
    docx = parse_scene_docx_lines(
        ("Scene 1: 1", "Asset 1: Red", "Scene 2: 2", "Asset 2: Green", "Asset 3: Blue")
    )
    for number, color in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(64, 48, QImage.Format.Format_ARGB32)
        image.fill(color)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (30, 30), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-PILOT-A-REAL-MP4",
        project_name="Synthetic Pilot A scene",
    )
    state = replace(state, settings=replace(state.settings, width=128, height=72))
    JsonProjectRepository().save(state, tmp_path / "pilot.angproj")
    frames = tmp_path / "frames"
    export_complete_still_sequence(state, frames, batch_size=30)
    return plan_silent_h264_mp4(state, frames, tmp_path / "pilot.mp4")


def _tools() -> dict[str, object]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    assert ffmpeg is not None, "Pilot A failed: ffmpeg executable missing"
    assert ffprobe is not None, "Pilot A failed: ffprobe executable missing"
    binary = Path(ffmpeg).resolve()
    probe = Path(ffprobe).resolve()
    return {
        "ffmpeg_path": binary,
        "ffmpeg_sha256": sha256_executable(binary),
        "ffprobe_path": probe,
        "ffprobe_sha256": sha256_executable(probe),
    }


def test_real_h264_mp4_probe_decode_and_sample_pixel(tmp_path: Path) -> None:
    plan = _fixture(tmp_path)
    tools = _tools()
    result = export_silent_h264_pilot_a(plan, **tools)
    assert result.path.is_file()
    assert result.frame_count == 60
    assert result.fps == 30
    assert (result.width, result.height) == (128, 72)
    assert abs(result.duration_seconds - 2) <= 1 / 30
    assert result.sha256 == hashlib.sha256(result.path.read_bytes()).hexdigest()
    assert result.file_bytes == result.path.stat().st_size
    assert len(result.rgb24_sha256) == 64
    frame = subprocess.run(
        [
            str(tools["ffmpeg_path"]),
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(result.path),
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=20,
        check=True,
    ).stdout
    assert len(frame) == 128 * 72 * 3
    assert frame[0] > 160 and frame[1] < 100 and frame[2] < 100
    output_dir = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
    if output_dir:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result.path, output / "ANG-Pilot-A-Real-H264.mp4")
        (output / "SHA256.txt").write_text(
            f"{result.sha256}  ANG-Pilot-A-Real-H264.mp4\n", encoding="utf-8"
        )


def test_wrong_ffmpeg_hash_is_refused_before_process(tmp_path: Path) -> None:
    plan = _fixture(tmp_path)
    tools = _tools()
    tools["ffmpeg_sha256"] = "0" * 64
    with pytest.raises(PilotAError):
        export_silent_h264_pilot_a(plan, **tools)
    assert not plan.destination.exists()


def test_existing_video_is_not_overwritten(tmp_path: Path) -> None:
    plan = _fixture(tmp_path)
    plan.destination.write_bytes(b"original must remain")
    with pytest.raises(PilotAError):
        export_silent_h264_pilot_a(plan, **_tools())
    assert plan.destination.read_bytes() == b"original must remain"


def test_cancel_before_launch_creates_no_video(tmp_path: Path) -> None:
    plan = _fixture(tmp_path)
    with pytest.raises(PilotAError):
        export_silent_h264_pilot_a(plan, should_cancel=lambda: True, **_tools())
    assert not plan.destination.exists()


def test_saved_project_to_real_mp4_without_external_preexported_frames(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _fixture(tmp_path)
    tools = _tools()
    destination = tmp_path / "full-project.mp4"
    monkeypatch.setenv("ANG_PILOT_A_FFMPEG", "1")
    status = scene_cli(
        [
            "mp4-pilot-a",
            "--project",
            str(tmp_path / "pilot.angproj"),
            "--output",
            str(destination),
            "--ffmpeg",
            str(tools["ffmpeg_path"]),
            "--ffmpeg-sha256",
            str(tools["ffmpeg_sha256"]),
            "--ffprobe",
            str(tools["ffprobe_path"]),
            "--ffprobe-sha256",
            str(tools["ffprobe_sha256"]),
            "--batch-size",
            "15",
        ]
    )
    assert status == 0
    assert "PASS MP4 PILOT A" in capsys.readouterr().out
    assert destination.is_file()
    assert destination.stat().st_size > 0
    assert not list(tmp_path.glob(".ang-still-mp4-*"))


def test_project_export_blocked_without_pilot_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fixture(tmp_path)
    monkeypatch.delenv("ANG_PILOT_A_FFMPEG", raising=False)
    state = JsonProjectRepository().load(tmp_path / "pilot.angproj")
    output = tmp_path / "not-authorized.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, output, **_tools())
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))


def test_project_export_cancellation_cleans_temporary_frames(tmp_path: Path) -> None:
    _fixture(tmp_path)
    state = JsonProjectRepository().load(tmp_path / "pilot.angproj")
    output = tmp_path / "cancelled.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, output, should_cancel=lambda: True, **_tools())
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))


def test_cli_missing_project_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tools = _tools()
    result = scene_cli(
        [
            "mp4-pilot-a",
            "--project",
            str(tmp_path / "missing.angproj"),
            "--output",
            str(tmp_path / "missing.mp4"),
            "--ffmpeg",
            str(tools["ffmpeg_path"]),
            "--ffmpeg-sha256",
            str(tools["ffmpeg_sha256"]),
            "--ffprobe",
            str(tools["ffprobe_path"]),
            "--ffprobe-sha256",
            str(tools["ffprobe_sha256"]),
        ]
    )
    assert result == 1
    assert not (tmp_path / "missing.mp4").exists()
    assert "GAGAL" in capsys.readouterr().err
