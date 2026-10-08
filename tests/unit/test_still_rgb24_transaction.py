"""INT-01G synthetic-only stage/discard lifecycle and deadline tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.infrastructure.still_rgb24_sink import (
    RGB24TransferCancelled,
    RGB24TransferError,
    RGB24TransferReceipt,
    RGB24TransferTimeout,
)
from ai_ngerti_geopolitik.infrastructure.still_rgb24_transaction import transfer_staged_rgb24
from tests.unit.test_still_rgb24_sink import _plan


class InMemoryStage:
    def __init__(self, *, fail_publish: bool = False) -> None:
        self.staged = bytearray()
        self.published: bytes | None = None
        self.discard_calls = 0
        self.fail_publish = fail_publish

    def write(self, data: bytes) -> int:
        self.staged.extend(data)
        return len(data)

    def publish(self, receipt: RGB24TransferReceipt) -> None:
        if self.fail_publish:
            raise OSError("sensitive private destination path")
        if len(self.staged) != receipt.byte_count:
            raise ValueError("staged bytes differ from receipt")
        self.published = bytes(self.staged)
        self.staged.clear()

    def discard(self) -> None:
        self.discard_calls += 1
        self.staged.clear()


def test_publish_only_after_complete_valid_transfer(tmp_path: Path) -> None:
    stage = InMemoryStage()
    plan = _plan(tmp_path)
    checkpoints: list[int] = []
    receipt = transfer_staged_rgb24(
        plan, stage, on_frame=lambda done, total: checkpoints.append(done)
    )
    assert receipt.frame_count == 5
    assert checkpoints == [1, 2, 3, 4, 5]
    assert stage.published is not None
    assert len(stage.published) == receipt.byte_count
    assert stage.discard_calls == 0
    assert not (tmp_path / "future.mp4").exists()


def test_cancel_discards_partial_staged_bytes(tmp_path: Path) -> None:
    stage = InMemoryStage()
    count = 0

    def frame(done: int, total: int) -> None:
        nonlocal count
        count = done

    with pytest.raises(RGB24TransferCancelled):
        transfer_staged_rgb24(
            _plan(tmp_path), stage, on_frame=frame, should_cancel=lambda: count >= 1
        )
    assert stage.published is None
    assert stage.discard_calls == 1
    assert not stage.staged


def test_timeout_discards_partial_stage(tmp_path: Path) -> None:
    stage = InMemoryStage()
    fake_time = [0.0]

    def progress(done: int, total: int) -> None:
        if done == 1:
            fake_time[0] = 2.0

    with pytest.raises(RGB24TransferTimeout):
        transfer_staged_rgb24(
            _plan(tmp_path), stage, timeout_seconds=1,
            monotonic=lambda: fake_time[0], on_frame=progress
        )
    assert stage.published is None
    assert stage.discard_calls == 1
    assert not stage.staged


def test_publish_failure_redacted_and_staging_discarded(tmp_path: Path) -> None:
    stage = InMemoryStage(fail_publish=True)
    with pytest.raises(RGB24TransferError) as error:
        transfer_staged_rgb24(_plan(tmp_path), stage)
    assert "sensitive" not in str(error.value)
    assert stage.discard_calls == 1
    assert stage.published is None
    assert not stage.staged
