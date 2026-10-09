"""Step 12-03F: native 120 truly distinct media files, resource and failure gates."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
from ctypes import wintypes
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter

from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.pilot_a_still_mp4 import sha256_executable
from ai_ngerti_geopolitik.infrastructure.still_project_mp4 import (
    StillProjectMP4Error,
    export_still_project_mp4,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("ANG_PILOT_A_FFMPEG") != "1",
    reason="Native FFmpeg integration runs only in owner-approved development Pilot A",
)


def _tools() -> dict[str, object]:
    import shutil

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    assert ffmpeg is not None and ffprobe is not None
    encoder = Path(ffmpeg).resolve()
    probe = Path(ffprobe).resolve()
    return {
        "ffmpeg_path": encoder,
        "ffmpeg_sha256": sha256_executable(encoder),
        "ffprobe_path": probe,
        "ffprobe_sha256": sha256_executable(probe),
    }


def _distinct_project(
    tmp_path: Path, fps: int
) -> tuple[ProjectState, tuple[tuple[int, int, int], ...]]:
    assert fps in (30, 60)
    frames_per_scene = 3 if fps == 30 else 4
    colors: list[tuple[int, int, int]] = []
    assets: list[Asset] = []
    clips: list[Clip] = []
    hashes: set[str] = set()
    for i in range(120):
        rgb = ((37 * i + 75) % 256, (79 * i + 40) % 256, (109 * i + 22) % 256)
        colors.append(rgb)
        image = QImage(64, 48, QImage.Format.Format_ARGB32)
        image.fill(0xFF000000 | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2])
        filename = tmp_path / f"distinct_{i:03d}.png"
        assert image.save(str(filename), "PNG")
        data = filename.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest not in hashes
        hashes.add(digest)
        name = f"MEDIA-{i:03d}"
        assets.append(
            Asset(
                asset_id=name,
                path_ref=str(filename.resolve()),
                media_type="image",
                duration=FrameTime(1, fps),
                width=64,
                height=48,
                has_audio=False,
                fingerprint_sha256=digest,
                source_name=filename.name,
                file_size=len(data),
            )
        )
        clips.append(
            Clip(
                clip_id=f"CLIP-{i:03d}",
                asset_id=name,
                timeline_start=FrameTime(i * frames_per_scene, fps),
                source_in=FrameTime(0, fps),
                source_out=FrameTime(1, fps),
                image_hold_frames=frames_per_scene,
            )
        )
    state = replace(
        ProjectState.create(
            f"P-120-UNIQUE-{fps}",
            "120 distinct source images",
            fps,
            width=128,
            height=72,
        ),
        assets=tuple(assets),
        tracks=(Track("V1", "video", 0, clips=tuple(clips)),),
    )
    state.validate()
    assert len(state.assets) == len(state.tracks[0].clips) == len(hashes) == 120
    return state, tuple(colors)


class _ProcessCounters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def _windows_working_set(pid: int) -> int:
    """Current physical working set in bytes for one Windows process."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessCounters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x0410, False, pid)
    if not handle:
        return 0
    try:
        counters = _ProcessCounters()
        counters.cb = ctypes.sizeof(_ProcessCounters)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return 0
        return int(counters.WorkingSetSize)
    finally:
        kernel.CloseHandle(handle)


@pytest.mark.parametrize(("fps", "hold"), [(30, 3), (60, 4)])
def test_real_mp4_120_distinct_pngs_frame_by_frame_and_windows_rss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fps: int, hold: int
) -> None:
    state, colors = _distinct_project(tmp_path, fps)
    output = tmp_path / f"unique-120-{fps}fps.mp4"
    native = _tools()
    assert state.timeline_end_frame == 120 * hold
    pid_lock = threading.Lock()
    child_pids: set[int] = set()
    original_popen = subprocess.Popen

    def capture_popen(*args, **kwargs):
        proc = original_popen(*args, **kwargs)
        with pid_lock:
            child_pids.add(proc.pid)
        return proc

    peak_parent = 0
    peak_children = 0
    peak_combined = 0
    observed = 0
    completed = threading.Event()

    def observe() -> None:
        nonlocal peak_parent, peak_children, peak_combined, observed
        while not completed.is_set():
            parent = _windows_working_set(os.getpid())
            with pid_lock:
                children = tuple(child_pids)
            child_sum = sum(_windows_working_set(pid) for pid in children)
            if parent:
                observed += 1
                peak_parent = max(peak_parent, parent)
                peak_children = max(peak_children, child_sum)
                peak_combined = max(peak_combined, parent + child_sum)
            completed.wait(0.04)

    if sys.platform == "win32":
        monkeypatch.setattr(subprocess, "Popen", capture_popen)
        monitor = threading.Thread(target=observe, daemon=True)
        monitor.start()
    else:
        monitor = None
    try:
        receipt = export_still_project_mp4(
            state, output, batch_size=30, timeout_seconds=420, **native
        )
    finally:
        completed.set()
        if monitor is not None:
            monitor.join(timeout=3)

    assert receipt.frame_count == 120 * hold
    assert receipt.fps == fps
    assert receipt.duration_seconds == pytest.approx(120 * hold / fps, abs=1 / fps)
    assert receipt.file_bytes == output.stat().st_size
    assert receipt.sha256 == hashlib.sha256(output.read_bytes()).hexdigest()
    assert receipt.file_bytes < 32 * 1024 * 1024
    if sys.platform == "win32":
        assert observed > 0
        assert peak_parent > 0
        assert peak_children > 0
        assert peak_combined >= peak_parent
        assert peak_combined < 1024 * 1024 * 1024
        print(
            f"WINDOWS RSS 120 unique {fps}fps: "
            f"parent={peak_parent // 1048576}MiB, "
            f"FFmpeg/FFprobe={peak_children // 1048576}MiB, "
            f"combined_sample_max={peak_combined // 1048576}MiB"
        )

    frame_bytes = receipt.width * receipt.height * 3
    center_offset = ((receipt.height // 2) * receipt.width + (receipt.width // 2)) * 3
    with tempfile.TemporaryFile() as rawvideo:
        result = subprocess.run(
            [
                str(native["ffmpeg_path"]),
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(output),
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
            stdout=rawvideo,
            stderr=subprocess.DEVNULL,
            timeout=45,
            check=False,
        )
        assert result.returncode == 0
        assert rawvideo.tell() == 120 * hold * frame_bytes
        for index, rgb in enumerate(colors):
            # Sample one interior frame from every one of the 120 clips.
            rawvideo.seek((index * hold + hold // 2) * frame_bytes + center_offset)
            pixel = rawvideo.read(3)
            assert len(pixel) == 3
            assert all(
                abs(actual - expected) <= 25 for actual, expected in zip(pixel, rgb, strict=True)
            )
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    assert not list(tmp_path.glob(".ang-pilot-*"))
    artifact_root = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
    if artifact_root:
        directory = Path(artifact_root)
        directory.mkdir(parents=True, exist_ok=True)
        name = f"ANG-Pilot-A-120-Distinct-{fps}FPS.mp4"
        import shutil

        shutil.copy2(output, directory / name)
        (directory / f"120-Distinct-{fps}FPS-SHA256.txt").write_text(
            f"{receipt.sha256}  {name}\n", encoding="utf-8"
        )
        if sys.platform == "win32":
            resource_evidence = {
                "kind": "ang-pilot-a-windows-sampled-working-set-v1",
                "total_unique_source_pngs": 120,
                "fps": fps,
                "output_frames": receipt.frame_count,
                "observations": observed,
                "parent_python_qt_sampled_max_bytes": peak_parent,
                "native_ffmpeg_ffprobe_sampled_max_bytes": peak_children,
                "combined_sampled_max_bytes": peak_combined,
                "rss_sample_limit_bytes": 1024 * 1024 * 1024,
                "sampling_seconds": 0.04,
                "limitations": (
                    "Windows current working-set samples; NOT a continuous native peak, "
                    "private bytes, disk peak, or proof of real-world 1080p/4K capacity"
                ),
            }
            (directory / f"ANG-Pilot-A-120-Distinct-{fps}FPS-RSS.json").write_text(
                json.dumps(resource_evidence, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )


def test_real_project_disk_full_during_manifest_write_discards_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state, _colors = _distinct_project(tmp_path, 30)
    output = tmp_path / "disk-full.mp4"
    original = Path.write_text
    writes = 0

    def disk_full(self: Path, data: str, *args, **kwargs) -> int:
        nonlocal writes
        if self.name == "manifest.json":
            writes += 1
            if writes == 3:
                raise OSError(errno.ENOSPC, "simulated no space left on device")
        return original(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", disk_full)
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, output, batch_size=10, **_tools())
    assert writes == 3
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    assert not list(tmp_path.glob(".angfull-*"))
    assert not list(tmp_path.glob(".angseq-*"))


def test_real_project_source_vanishes_after_some_frames_fails_closed(tmp_path: Path) -> None:
    state, _colors = _distinct_project(tmp_path, 30)
    output = tmp_path / "missing-input.mp4"
    missing = Path(state.asset("MEDIA-009").path_ref)
    calls = 0

    def remove_after_start() -> bool:
        nonlocal calls
        calls += 1
        if calls == 20:
            missing.unlink()
        return False

    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(
            state,
            output,
            batch_size=20,
            should_cancel=remove_after_start,
            **_tools(),
        )
    assert calls >= 20
    assert not missing.exists()
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))


def test_complete_manifest_cancel_after_write_prevents_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cancellation at full-project publication boundary cannot leak a manifest."""
    state, _ = _distinct_project(tmp_path, 30)
    first_clip = state.tracks[0].clips[0]
    state = replace(
        state,
        assets=(state.assets[0],),
        tracks=(replace(state.tracks[0], clips=(first_clip,)),),
    )
    state.validate()
    stop = threading.Event()
    original = Path.write_text
    master_written = 0

    def flag_cancellation(self: Path, data: str, *args, **kwargs) -> int:
        nonlocal master_written
        result = original(self, data, *args, **kwargs)
        if '"format": "ang-still-project-v1"' in data:
            master_written += 1
            stop.set()
        return result

    monkeypatch.setattr(Path, "write_text", flag_cancellation)
    output = tmp_path / "cancel-on-manifest.mp4"
    with pytest.raises(StillProjectMP4Error):
        export_still_project_mp4(state, output, batch_size=1, should_cancel=stop.is_set, **_tools())
    assert master_written == 1
    assert stop.is_set()
    assert not output.exists()
    assert not list(tmp_path.glob(".ang-still-mp4-*"))
    assert not list(tmp_path.glob(".angfull-*"))
    assert not list(tmp_path.glob(".angseq-*"))



def _fullhd_project(
    root: Path, fps: int
) -> tuple[ProjectState, tuple[tuple[tuple[int, int, int], ...], ...]]:
    """16 different patterned 1080p source files, with three sampled pixels each."""
    assert fps in (30, 60)
    assets: list[Asset] = []
    clips: list[Clip] = []
    expected: list[tuple[tuple[int, int, int], ...]] = []
    sha_values: set[str] = set()
    sample_points = ((320, 180), (960, 540), (1600, 900))
    for i in range(16):
        image = QImage(1920, 1080, QImage.Format.Format_RGB32)
        assert not image.isNull()
        start = QColor((i * 67 + 20) % 256, (i * 23 + 55) % 256, (i * 97 + 70) % 256)
        end = QColor((i * 31 + 160) % 256, (i * 107 + 45) % 256, (i * 43 + 135) % 256)
        gradient = QLinearGradient(0, 0, 1920, 1080)
        gradient.setColorAt(0.0, start)
        gradient.setColorAt(1.0, end)
        painter = QPainter(image)
        try:
            painter.fillRect(image.rect(), gradient)
            for stripe in range(9):
                painter.fillRect(
                    (i * 41 + stripe * 193) % 1920,
                    (i * 63 + stripe * 131) % 1080,
                    40 + stripe * 7,
                    80 + stripe * 13,
                    QColor(
                        (i * 43 + stripe * 23) % 256,
                        (i * 27 + stripe * 73) % 256,
                        (i * 19 + stripe * 37) % 256,
                        165,
                    ),
                )
            painter.setPen(QColor(245, 235, 205))
            painter.drawEllipse(140 + i * 13, 110 + i * 11, 120 + i * 3, 180 + i * 4)
        finally:
            painter.end()
        expected.append(
            tuple(
                (
                    image.pixelColor(x, y).red(),
                    image.pixelColor(x, y).green(),
                    image.pixelColor(x, y).blue(),
                )
                for x, y in sample_points
            )
        )
        asset_file = root / f"1080p_original_{i:02d}.png"
        assert image.save(str(asset_file), "PNG")
        file_data = asset_file.read_bytes()
        digest = hashlib.sha256(file_data).hexdigest()
        assert digest not in sha_values
        sha_values.add(digest)
        asset_id = f"HD-IMAGE-{i:02d}"
        assets.append(
            Asset(
                asset_id=asset_id,
                path_ref=str(asset_file.resolve()),
                media_type="image",
                duration=FrameTime(1, fps),
                width=1920,
                height=1080,
                has_audio=False,
                fingerprint_sha256=digest,
                source_name=asset_file.name,
                file_size=len(file_data),
            )
        )
        clips.append(
            Clip(
                clip_id=f"HD-CLIP-{i:02d}",
                asset_id=asset_id,
                timeline_start=FrameTime(2 * i, fps),
                source_in=FrameTime(0, fps),
                source_out=FrameTime(1, fps),
                image_hold_frames=2,
            )
        )
    state = replace(
        ProjectState.create(
            f"P-HD-PILOT-{fps}", "Sixteen different Full HD sources", fps
        ),
        assets=tuple(assets),
        tracks=(Track("V1", "video", 0, clips=tuple(clips)),),
    )
    state.validate()
    assert state.timeline_end_frame == 32
    assert len(sha_values) == 16
    return state, tuple(expected)


@pytest.mark.parametrize("fps", [30, 60])
def test_real_1080p_patterned_unique_media_and_windows_native_rss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fps: int
) -> None:
    """Real 1920×1080 H264 from 16 separate varied originals at 30/60 fps."""
    state, expected = _fullhd_project(tmp_path, fps)
    output = tmp_path / f"fullhd-unique-{fps}fps.mp4"
    native = _tools()
    original_popen = subprocess.Popen
    processes: set[int] = set()
    lock = threading.Lock()
    stop = threading.Event()
    measures = {"parent": 0, "native": 0, "combined": 0, "samples": 0}

    def popen_observed(*args, **kwargs):
        child = original_popen(*args, **kwargs)
        with lock:
            processes.add(child.pid)
        return child

    def sample_rss() -> None:
        while not stop.is_set():
            parent = _windows_working_set(os.getpid())
            with lock:
                observed_pids = tuple(processes)
            native = sum(_windows_working_set(pid) for pid in observed_pids)
            if parent:
                measures["samples"] += 1
                measures["parent"] = max(measures["parent"], parent)
                measures["native"] = max(measures["native"], native)
                measures["combined"] = max(measures["combined"], parent + native)
            stop.wait(0.04)

    if sys.platform == "win32":
        monkeypatch.setattr(subprocess, "Popen", popen_observed)
        sampler = threading.Thread(target=sample_rss, daemon=True)
        sampler.start()
    else:
        sampler = None
    try:
        receipt = export_still_project_mp4(
            state,
            output,
            batch_size=8,
            timeout_seconds=420,
            **native,
        )
    finally:
        stop.set()
        if sampler is not None:
            sampler.join(timeout=5)
            assert not sampler.is_alive()
    assert receipt.frame_count == 32
    assert receipt.fps == fps
    assert (receipt.width, receipt.height) == (1920, 1080)
    assert receipt.duration_seconds == pytest.approx(32 / fps, abs=1 / fps)
    assert receipt.sha256 == hashlib.sha256(output.read_bytes()).hexdigest()
    assert 0 < output.stat().st_size < 128 * 1024 * 1024
    assert not list(tmp_path.glob(".ang-still-mp4-*"))

    if sys.platform == "win32":
        assert measures["samples"] > 0
        assert measures["parent"] > 0
        assert measures["native"] > 0
        assert measures["combined"] >= measures["parent"]
        assert measures["combined"] < 2 * 1024 * 1024 * 1024

    probe = subprocess.run(
        [
            str(native["ffprobe_path"]),
            "-v",
            "error",
            "-count_frames",
            "-show_entries",
            "stream=width,height,codec_name,avg_frame_rate,nb_read_frames",
            "-of",
            "json",
            str(output),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=True,
        timeout=35,
    )
    stream = json.loads(probe.stdout)["streams"][0]
    assert stream["codec_name"] == "h264"
    assert (int(stream["width"]), int(stream["height"])) == (1920, 1080)
    assert stream["avg_frame_rate"] == f"{fps}/1"
    assert int(stream["nb_read_frames"]) == 32

    # Decode all 32 actual full-HD H264 frames to on-disk scratch, not RAM.
    # Read exact source-matched pixels from every original scene.
    frame_size = 1920 * 1080 * 3
    coords = ((320, 180), (960, 540), (1600, 900))
    with tempfile.TemporaryFile() as decoded:
        result = subprocess.run(
            [
                str(native["ffmpeg_path"]),
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(output),
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
            stdout=decoded,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=60,
        )
        assert result.returncode == 0
        assert decoded.tell() == 32 * frame_size
        for image_index, samples in enumerate(expected):
            for frame_in_clip in (0, 1):
                for (x, y), pixel_expected in zip(coords, samples, strict=True):
                    offset = (
                        (image_index * 2 + frame_in_clip) * frame_size
                        + (y * 1920 + x) * 3
                    )
                    decoded.seek(offset)
                    rgb = decoded.read(3)
                    assert len(rgb) == 3
                    assert all(
                        abs(int(actual) - int(wanted)) <= 35
                        for actual, wanted in zip(rgb, pixel_expected, strict=True)
                    )

    artifact_dir = os.environ.get("ANG_PILOT_A_OUTPUT_DIR")
    if artifact_dir:
        directory = Path(artifact_dir)
        directory.mkdir(parents=True, exist_ok=True)
        import shutil

        name = f"ANG-Pilot-A-1080p-16Images-{fps}FPS.mp4"
        shutil.copy2(output, directory / name)
        (directory / f"1080p-{fps}FPS-SHA256.txt").write_text(
            f"{receipt.sha256}  {name}\n", encoding="utf-8"
        )
        if sys.platform == "win32":
            evidence = {
                "scope": "16 separate patterned original Full HD images, 32 H264 frames",
                "fps": fps,
                "resolution": "1920x1080",
                "samples": measures["samples"],
                "qt_python_process_working_set_max_sampled_bytes": measures["parent"],
                "ffmpeg_ffprobe_working_set_max_sampled_bytes": measures["native"],
                "combined_working_set_max_sampled_bytes": measures["combined"],
                "sample_period_seconds": 0.04,
                "bound_bytes": 2 * 1024 * 1024 * 1024,
                "limitations": (
                    "Working-set samples only; not total peak/native private bytes, "
                    "not a real photo corpus and not 300-scene production stress"
                ),
            }
            (directory / f"1080p-{fps}FPS-Windows-RSS.json").write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
