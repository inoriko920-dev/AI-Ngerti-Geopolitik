"""Real native FFmpeg Pilot A: synthetic image-only H.264 MP4 on Windows."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import wave
from array import array
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.bootstrap.scene_cli import main as scene_cli
from ai_ngerti_geopolitik.bootstrap.w8_controller import W8IntentRouter, W8RuntimeController
from ai_ngerti_geopolitik.domain import (
    Asset,
    FrameTime,
    NarrationTrack,
    SubtitleCue,
    SubtitleStyle,
    SubtitleTrack,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
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
from ai_ngerti_geopolitik.infrastructure.still_project_mp4 import (
    StillProjectMP4Error,
    export_still_project_mp4,
)
from ai_ngerti_geopolitik.presentation.main_window import create_main_window
from ai_ngerti_geopolitik.presentation.navigation import UiRoute

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


def test_real_frozen_gui_export_button_produces_verified_mp4(
    qtbot: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Complete Windows UI click → native FFmpeg → verified full-HD MP4."""
    docx = parse_scene_docx_lines(("Scene 1: 1", "Asset 1: Red"))
    img = QImage(64, 48, QImage.Format.Format_ARGB32)
    img.fill(0xFFFF0000)
    assert img.save(str(tmp_path / "A001.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (1,), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-GUI-NATIVE-PILOT",
        project_name="Real UI native MP4 test",
    )
    assert (state.settings.width, state.settings.height) == (1920, 1080)
    project = tmp_path / "gui-real.angproj"
    JsonProjectRepository().save(state, project)
    monkeypatch.setenv("ANG_PILOT_A_FFMPEG", "1")
    router = W8IntentRouter()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=router)
    qtbot.addWidget(window.window)
    controller = W8RuntimeController(window, timer_enabled=False)
    router.delegate = controller.handle
    controller.session.open_project(project)
    window.show()
    window.show_route(UiRoute.EXPORT_SETTINGS)
    dialog = window._active_dialog
    assert dialog is not None
    folder = dialog.findChild(QLineEdit, "field_export_directory")
    filename = dialog.findChild(QLineEdit, "field_export_name")
    assert folder is not None and filename is not None
    folder.setText(str(tmp_path))
    filename.setText("gui-native-verified")
    boxes = dialog.findChildren(QComboBox)
    assert len(boxes) == 6
    boxes[-1].setCurrentText("Tanpa Subtitle")
    button = dialog.findChild(QPushButton, "btn_export_render")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    def done() -> bool:
        controller.poll()
        return controller.export_future is None

    try:
        qtbot.waitUntil(done, timeout=90000)
        assert "terverifikasi" in controller.last_error
        actual = tmp_path / "gui-native-verified.mp4"
        assert actual.is_file() and actual.stat().st_size > 0
        probe = subprocess.run(
            [
                str(_tools()["ffprobe_path"]),
                "-v",
                "error",
                "-show_entries",
                "stream=codec_name,width,height",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                str(actual),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=20,
            check=True,
            text=True,
        )
        assert probe.stdout.splitlines() == ["h264", "1920", "1080"]
        output_dir = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
        if output_dir:
            target = Path(output_dir)
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(actual, target / "ANG-Pilot-A-GUI-Real-H264.mp4")
            digest = hashlib.sha256(actual.read_bytes()).hexdigest()
            (target / "GUI-SHA256.txt").write_text(
                f"{digest}  ANG-Pilot-A-GUI-Real-H264.mp4\n", encoding="utf-8"
            )
    finally:
        controller.shutdown()
        window.close()


def _audio_state(tmp_path: Path, *, with_subtitles: bool):
    _fixture(tmp_path)
    state = JsonProjectRepository().load(tmp_path / "pilot.angproj")
    narration = tmp_path / "narration.wav"
    with wave.open(str(narration), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(48000)
        # A nonzero deterministic test signal, not a credential or private recording.
        audio.writeframes((b"\x40\x1f" * 240 + b"\xc0\xe0" * 240) * 200)
    voice = Asset(
        asset_id="A004",
        path_ref=str(narration.resolve()),
        media_type="audio",
        duration=FrameTime(60, 30),
        width=0,
        height=0,
        has_audio=True,
        fingerprint_sha256=hashlib.sha256(narration.read_bytes()).hexdigest(),
        file_size=narration.stat().st_size,
        sample_rate=48000,
    )
    subtitle = (
        SubtitleTrack(
            source_ref="synthetic-test.srt",
            cues=(
                SubtitleCue(
                    cue_id="CUE001",
                    index=1,
                    start=FrameTime(0, 30),
                    end=FrameTime(60, 30),
                    text="TEST CAPTION",
                ),
            ),
            style=SubtitleStyle(font_family="Arial", font_size=16, margin_v=8),
        )
        if with_subtitles
        else None
    )
    result = replace(
        state,
        assets=(*state.assets, voice),
        narration=NarrationTrack("N001", "A004", FrameTime(0, 30)),
        subtitle=subtitle,
    )
    result.validate()
    return result


def _probe_av(destination: Path, tool: Path) -> dict:
    result = subprocess.run(
        [
            str(tool),
            "-v",
            "error",
            "-count_frames",
            "-show_entries",
            "stream=codec_type,codec_name,nb_read_frames",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(destination),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        text=True,
        timeout=20,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("subtitles", [False, True])
def test_real_wav_narration_and_optional_burned_subtitle(tmp_path: Path, subtitles: bool) -> None:
    from ai_ngerti_geopolitik.infrastructure.still_project_mp4 import export_still_project_mp4

    state = _audio_state(tmp_path, with_subtitles=subtitles)
    dest = tmp_path / ("narration_subtitles.mp4" if subtitles else "narration_only.mp4")
    native = _tools()
    result = export_still_project_mp4(
        state,
        dest,
        include_subtitles=subtitles,
        batch_size=15,
        **native,
    )
    assert result.path == dest
    assert dest.is_file() and dest.stat().st_size > 0
    streams = _probe_av(dest, native["ffprobe_path"])["streams"]
    assert sum(stream["codec_name"] == "h264" for stream in streams) == 1
    assert sum(stream["codec_name"] == "aac" for stream in streams) == 1
    assert next(s["nb_read_frames"] for s in streams if s["codec_name"] == "h264") == "60"
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    if subtitles:
        root = Path(os.environ.get("ANG_PILOT_A_OUTPUT_DIR", str(tmp_path)))
        root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, root / "ANG-Pilot-A-WAV-Burned-Caption.mp4")
        (root / "AV-SHA256.txt").write_text(
            f"{result.sha256}  ANG-Pilot-A-WAV-Burned-Caption.mp4\n",
            encoding="utf-8",
        )


def test_narration_fingerprint_tamper_never_publishes_mp4(tmp_path: Path) -> None:
    from ai_ngerti_geopolitik.infrastructure.still_project_mp4 import (
        StillProjectMP4Error,
        export_still_project_mp4,
    )

    state = _audio_state(tmp_path, with_subtitles=False)
    wav_path = tmp_path / "narration.wav"
    wav_path.write_bytes(wav_path.read_bytes() + b"x")
    destination = tmp_path / "no-tamper.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, destination, **_tools())
    assert not destination.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))


def test_real_mp3_narration_respects_half_second_timeline_offset(tmp_path: Path) -> None:
    """Actual libmp3lame input -> AAC output; validate silence then audible PCM."""
    state = _audio_state(tmp_path, with_subtitles=False)
    tools = _tools()
    mp3 = tmp_path / "voice.mp3"
    conversion = subprocess.run(
        [
            str(tools["ffmpeg_path"]),
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(tmp_path / "narration.wav"),
            "-vn",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            "-y",
            str(mp3),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=20,
    )
    assert conversion.returncode == 0 and mp3.is_file()
    source = replace(
        state.asset("A004"),
        path_ref=str(mp3.resolve()),
        fingerprint_sha256=hashlib.sha256(mp3.read_bytes()).hexdigest(),
        file_size=mp3.stat().st_size,
    )
    assert state.narration is not None
    delayed = replace(
        state,
        assets=tuple(source if a.asset_id == source.asset_id else a for a in state.assets),
        narration=replace(state.narration, timeline_start=FrameTime(15, 30)),
    )
    delayed.validate()
    output = tmp_path / "mp3-offset.mp4"
    result = export_still_project_mp4(delayed, output, **tools, batch_size=15)
    assert result.path == output
    streams = _probe_av(output, tools["ffprobe_path"])["streams"]
    assert sum(s["codec_name"] == "aac" for s in streams) == 1
    raw = subprocess.run(
        [
            str(tools["ffmpeg_path"]),
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(output),
            "-map",
            "0:a:0",
            "-ar",
            "8000",
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=30,
        check=True,
    ).stdout
    samples = array("h")
    samples.frombytes(raw)
    assert len(samples) >= 14000
    quiet = max(abs(value) for value in samples[400:2000])
    audible = max(abs(value) for value in samples[6400:8000])
    assert quiet < 500
    assert audible > 1000
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    target_path = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
    if target_path:
        artifact_dir = Path(target_path)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, artifact_dir / "ANG-Pilot-A-MP3-Offset-H264.mp4")
        (artifact_dir / "MP3-SHA256.txt").write_text(
            f"{result.sha256}  ANG-Pilot-A-MP3-Offset-H264.mp4\n", encoding="utf-8"
        )


def test_real_unicode_burned_subtitle_appears_only_in_cue_window(tmp_path: Path) -> None:
    """An actual Unicode caption changes pixels during its frame-exact cue."""
    state = _audio_state(tmp_path, with_subtitles=True)
    subtitle = state.subtitle
    assert subtitle is not None
    cue = replace(
        subtitle.cues[0],
        start=FrameTime(5, 30),
        end=FrameTime(25, 30),
        text="Café 日本",
    )
    state = replace(state, subtitle=replace(subtitle, cues=(cue,)))
    state.validate()
    tools = _tools()
    destination = tmp_path / "unicode-caption.mp4"
    receipt = export_still_project_mp4(
        state, destination, include_subtitles=True, batch_size=15, **tools
    )
    assert receipt.frame_count == 60
    raw = subprocess.run(
        [
            str(tools["ffmpeg_path"]),
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(destination),
            "-map",
            "0:v:0",
            "-an",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "-",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
        timeout=30,
    ).stdout
    frame_bytes = receipt.width * receipt.height * 3
    assert len(raw) == frame_bytes * 60

    def pixels(frame: int) -> bytes:
        return raw[frame * frame_bytes : (frame + 1) * frame_bytes]

    before, during, after = pixels(0), pixels(12), pixels(28)
    changed_during = sum(abs(x - y) > 25 for x, y in zip(before, during, strict=True))
    changed_after = sum(abs(x - y) > 25 for x, y in zip(before, after, strict=True))
    assert changed_during > 30
    assert changed_after < changed_during // 2


def test_rejects_control_character_caption_without_final_mp4(tmp_path: Path) -> None:
    state = _audio_state(tmp_path, with_subtitles=True)
    assert state.subtitle is not None
    cue = replace(state.subtitle.cues[0], text="Safe\u202eunsafe")
    invalid = replace(state, subtitle=replace(state.subtitle, cues=(cue,)))
    output = tmp_path / "reject-bidi.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(invalid, output, include_subtitles=True, **_tools())
    assert not output.exists()



def test_vbr_mp3_long_timeline_and_multicue_srt_sync(tmp_path: Path) -> None:
    """12s real FFmpeg render: SRT cue windows and 1s delayed VBR MP3 narration."""
    from ai_ngerti_geopolitik.application.subtitle_import import build_subtitle_track
    from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser

    state = _audio_state(tmp_path, with_subtitles=False)
    assert state.narration is not None
    # Extend the last image HOLD: preserve original image identities and content hashes.
    track = state.tracks[0]
    assert track.clips
    extended = replace(track.clips[-1], image_hold_frames=330)
    state = replace(
        state,
        tracks=(replace(track, clips=(*track.clips[:-1], extended)),),
    )
    assert state.timeline_end_frame == 360
    native = _tools()
    source_mp3 = tmp_path / "narration-vbr.mp3"
    cmd = [
        str(native["ffmpeg_path"]),
        "-nostdin",
        "-v",
        "error",
        "-i",
        str(tmp_path / "narration.wav"),
        "-c:a",
        "libmp3lame",
        "-q:a",
        "5",
        "-y",
        str(source_mp3),
    ]
    encoded = subprocess.run(
        cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, timeout=20, check=False
    )
    assert encoded.returncode == 0 and source_mp3.is_file()
    audio_asset = replace(
        state.asset("A004"),
        path_ref=str(source_mp3.resolve()),
        file_size=source_mp3.stat().st_size,
        fingerprint_sha256=hashlib.sha256(source_mp3.read_bytes()).hexdigest(),
    )
    state = replace(
        state,
        assets=tuple(audio_asset if a.asset_id == "A004" else a for a in state.assets),
        narration=replace(state.narration, timeline_start=FrameTime(30, 30)),
    )
    text = (
        "\ufeff1\r\n00:00:00,500 --> 00:00:01,500\r\nCafé\r\n\r\n"
        "2\r\n00:00:04,000 --> 00:00:05,000\r\nIndonesia 2026\r\n\r\n"
        "3\r\n00:00:10,000 --> 00:00:11,000\r\n日本\r\n"
    )
    source_srt = tmp_path / "narration-multi.srt"
    source_srt.write_bytes(text.encode("utf-8"))
    original_digest = hashlib.sha256(source_srt.read_bytes()).hexdigest()
    subtitle = build_subtitle_track(
        state, source_srt, Utf8SrtParser().parse(source_srt)
    )
    state = replace(
        state,
        subtitle=replace(
            subtitle,
            style=SubtitleStyle(font_family="Arial", font_size=16, margin_v=8),
        ),
    )
    state.validate()
    result_path = tmp_path / "long-vbr-and-srt.mp4"
    result = export_still_project_mp4(
        state, result_path, batch_size=60, include_subtitles=True, **native
    )
    assert result.frame_count == 360
    assert abs(result.duration_seconds - 12.0) <= 1 / 30
    assert hashlib.sha256(source_srt.read_bytes()).hexdigest() == original_digest
    verified = _probe_av(result_path, native["ffprobe_path"])
    streams = verified["streams"]
    assert next(s["nb_read_frames"] for s in streams if s["codec_name"] == "h264") == "360"
    assert sum(s["codec_name"] == "aac" for s in streams) == 1
    audio = subprocess.run(
        [
            str(native["ffmpeg_path"]), "-nostdin", "-v", "error",
            "-i", str(result_path), "-map", "0:a:0", "-ar", "8000",
            "-ac", "1", "-f", "s16le", "-",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=35,
        check=True,
    ).stdout
    samples = array("h")
    samples.frombytes(audio)
    assert len(samples) >= 88000
    assert max(abs(x) for x in samples[1600:4000]) < 500
    assert max(abs(x) for x in samples[12000:14400]) > 1000
    assert max(abs(x) for x in samples[72000:76000]) < 500

    # Decode just 6 frames, avoiding huge frame buffers; check 3 separated SRT cues.
    frames: list[bytes] = []
    for frame_index in (1, 30, 90, 135, 285, 315):
        image_bytes = subprocess.run(
            [
                str(native["ffmpeg_path"]), "-nostdin", "-v", "error",
                "-i", str(result_path), "-vf",
                f"select=eq(n\\,{frame_index})", "-vsync", "0",
                "-frames:v", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=25,
            check=True,
        ).stdout
        assert len(image_bytes) == result.width * result.height * 3
        frames.append(image_bytes)
    # Still background alternates by source HOLD; compare only adjacent
    # frames within the same clip when testing a subtitle's presence.
    assert len(frames) == 6
    assert frames[0] != frames[1]
    assert frames[2] != frames[3]
    assert frames[4] != frames[5]
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    target = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
    if target:
        directory = Path(target)
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result_path, directory / "ANG-Pilot-A-12s-VBR-MultiSRT.mp4")
        (directory / "12S-SHA256.txt").write_text(
            f"{result.sha256}  ANG-Pilot-A-12s-VBR-MultiSRT.mp4\n",
            encoding="utf-8",
        )


def test_native_narration_metadata_mismatch_never_publishes(tmp_path: Path) -> None:
    state = _audio_state(tmp_path, with_subtitles=False)
    incorrect = replace(state.asset("A004"), sample_rate=44100)
    state = replace(
        state,
        assets=tuple(incorrect if a.asset_id == "A004" else a for a in state.assets),
    )
    state.validate()
    output = tmp_path / "invalid-audio-metadata.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, output, **_tools())
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
