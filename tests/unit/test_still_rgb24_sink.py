"""INT-01F: bounded sink handoff using in-process fake sinks only."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import export_complete_still_sequence
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import plan_silent_h264_mp4
from ai_ngerti_geopolitik.infrastructure.still_rgb24_sink import (
    RGB24TransferCancelled,
    RGB24TransferError,
    RGB24TransferTimeout,
    feed_rgb24_to_sink,
)
from ai_ngerti_geopolitik.infrastructure.still_rgb24_stream import iter_rgb24_chunks


class MemorySink:
    def __init__(self, *, max_write: int = 100_000) -> None:
        self.data = bytearray()
        self.max_write = max_write
        self.calls = 0

    def write(self, data: bytes) -> int:
        self.calls += 1
        n = min(len(data), self.max_write)
        self.data.extend(data[:n])
        return n


class NoProgressSink:
    def write(self, data: bytes) -> int:
        return 0


class OverreportSink:
    def write(self, data: bytes) -> int:
        return len(data) + 1


class BooleanSink:
    def write(self, data: bytes) -> int:
        return True


class FaultSink:
    def write(self, data: bytes) -> int:
        raise OSError("private file path must not leak")


def _plan(tmp_path: Path):
    docx = parse_scene_docx_lines(
        ("Scene 1: 1", "Asset 1: Red", "Scene 2: 2", "Asset 2: Green", "Asset 3: Blue")
    )
    for number, color in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(color)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (2, 3), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-RGB24-SINK",
        project_name="Bounded sink test",
    )
    state = replace(state, settings=replace(state.settings, width=14, height=8))
    folder = tmp_path / "frames"
    export_complete_still_sequence(state, folder, batch_size=2)
    return plan_silent_h264_mp4(state, folder, tmp_path / "future.mp4")


def test_full_transfer_short_writes_progress_checksum(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink(max_write=7)
    notifications: list[tuple[int, int]] = []
    receipt = feed_rgb24_to_sink(
        plan, sink, chunk_rows=2, on_frame=lambda done, total: notifications.append((done, total))
    )
    expected = b"".join(iter_rgb24_chunks(plan, chunk_rows=1))
    assert bytes(sink.data) == expected
    assert receipt.byte_count == 5 * (14 * 8 * 3)
    assert receipt.frame_count == 5
    assert receipt.fps == 30
    assert receipt.stream_sha256 == hashlib.sha256(expected).hexdigest()
    assert notifications == [(number, 5) for number in range(1, 6)]
    assert sink.calls > 5
    assert not (tmp_path / "future.mp4").exists()


def test_cancel_before_first_byte_no_sink_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink()
    with pytest.raises(RGB24TransferCancelled):
        feed_rgb24_to_sink(plan, sink, should_cancel=lambda: True)
    assert not sink.data


def test_cancel_after_complete_frame_requires_discard(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink(max_write=30)
    completed = 0

    def progress(done: int, total: int) -> None:
        nonlocal completed
        completed = done

    with pytest.raises(RGB24TransferCancelled):
        feed_rgb24_to_sink(
            plan, sink, chunk_rows=1, should_cancel=lambda: completed >= 1, on_frame=progress
        )
    assert completed == 1
    assert len(sink.data) == plan.rgb24_bytes_per_frame
    assert not (tmp_path / "future.mp4").exists()


@pytest.mark.parametrize("bad_sink", (NoProgressSink, OverreportSink, BooleanSink, FaultSink))
def test_hostile_sink_fails_closed_without_path_leak(tmp_path: Path, bad_sink) -> None:
    plan = _plan(tmp_path)
    with pytest.raises(RGB24TransferError) as failure:
        feed_rgb24_to_sink(plan, bad_sink())
    assert "private" not in str(failure.value)
    assert not (tmp_path / "future.mp4").exists()


def test_late_png_change_detected_before_next_frame(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink()

    def update_file(done: int, total: int) -> None:
        if done == 2:
            plan.verified_frames.frame_files[2].write_bytes(b"tampered frame")

    with pytest.raises(RGB24TransferError):
        feed_rgb24_to_sink(plan, sink, on_frame=update_file)
    assert len(sink.data) == plan.rgb24_bytes_per_frame * 2


def test_corrupt_contract_and_row_guard(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    with pytest.raises(RGB24TransferError):
        feed_rgb24_to_sink(replace(plan, rgb24_bytes_per_frame=1), MemorySink())
    with pytest.raises(RGB24TransferError):
        feed_rgb24_to_sink(plan, MemorySink(), chunk_rows=0)


@pytest.mark.parametrize("budget", (0, -1, True, float("inf"), float("nan"), 90_000))
def test_invalid_timeout_budget_rejected_without_writes(tmp_path: Path, budget) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink()
    with pytest.raises(RGB24TransferError, match="budget"):
        feed_rgb24_to_sink(plan, sink, timeout_seconds=budget)
    assert not sink.data


def test_timed_write_exceeding_budget_fails_after_write_returns(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    elapsed = [0.0]

    class SlowSink(MemorySink):
        def write(self, data: bytes) -> int:
            elapsed[0] += 2.0
            return super().write(data)

    sink = SlowSink(max_write=7)
    with pytest.raises(RGB24TransferTimeout):
        feed_rgb24_to_sink(
            plan, sink, timeout_seconds=1.0, monotonic=lambda: elapsed[0]
        )
    assert 0 < len(sink.data) < plan.rgb24_bytes_per_frame
    assert not (tmp_path / "future.mp4").exists()


def test_timeout_between_frames_and_no_false_receipt(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    elapsed = [0.0]
    sink = MemorySink()

    def progress(done: int, total: int) -> None:
        if done == 1:
            elapsed[0] = 1.5

    with pytest.raises(RGB24TransferTimeout):
        feed_rgb24_to_sink(
            plan, sink, on_frame=progress, timeout_seconds=1.0,
            monotonic=lambda: elapsed[0]
        )
    assert len(sink.data) == plan.rgb24_bytes_per_frame


def test_normal_budget_and_fake_clock_yield_identical_checksum(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    sink = MemorySink(max_write=5)
    receipt = feed_rgb24_to_sink(
        plan, sink, timeout_seconds=1.0, monotonic=lambda: 10.0
    )
    assert receipt.frame_count == 5
    assert receipt.stream_sha256 == hashlib.sha256(sink.data).hexdigest()
