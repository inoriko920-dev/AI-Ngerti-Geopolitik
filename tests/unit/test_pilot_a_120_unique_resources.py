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
from PySide6.QtGui import QImage

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
