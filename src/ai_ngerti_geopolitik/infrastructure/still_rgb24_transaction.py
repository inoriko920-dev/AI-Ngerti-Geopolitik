"""A two-phase synthetic RGB24 sink transaction, without native process work.

The caller supplies an already-staged sink. A receipt is not a valid MP4 and
does not permit output publishing. The sink's publish() is an abstract hook;
tests provide only in-memory fakes. Future native usage requires Pilot A.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Protocol

from ai_ngerti_geopolitik.infrastructure.still_h264_plan import SilentH264Plan
from ai_ngerti_geopolitik.infrastructure.still_rgb24_sink import (
    RGB24Sink,
    RGB24TransferCancelled,
    RGB24TransferError,
    RGB24TransferReceipt,
    RGB24TransferTimeout,
    feed_rgb24_to_sink,
)


class StagedRGB24Sink(RGB24Sink, Protocol):
    """Mockable interface: publish atomically or discard all staged bytes."""

    def publish(self, receipt: RGB24TransferReceipt) -> None: ...

    def discard(self) -> None: ...


def transfer_staged_rgb24(
    plan: SilentH264Plan,
    stage: StagedRGB24Sink,
    *,
    should_cancel: Callable[[], bool] | None = None,
    on_frame: Callable[[int, int], None] | None = None,
    timeout_seconds: float | None = None,
    monotonic: Callable[[], float] | None = None,
) -> RGB24TransferReceipt:
    """Transfer then publish only after a verified receipt; discard on all failures.

    This module cannot guarantee that a foreign sink publishes atomically.
    The test fake honors this contract; production native implementation is
    explicitly not approved and must independently verify actual MP4 output.
    """
    published = False
    clock = monotonic if monotonic is not None else time.monotonic

    def safe_clock() -> float:
        try:
            reading = clock()
            if not math.isfinite(reading):
                raise ValueError("invalid clock reading")
        except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
            raise RGB24TransferTimeout("RGB24 pre-publication clock failed") from None
        return reading

    try:
        started = safe_clock() if timeout_seconds is not None else 0.0
        if monotonic is None:
            receipt = feed_rgb24_to_sink(
                plan,
                stage,
                should_cancel=should_cancel,
                on_frame=on_frame,
                timeout_seconds=timeout_seconds,
            )
        else:
            receipt = feed_rgb24_to_sink(
                plan,
                stage,
                should_cancel=should_cancel,
                on_frame=on_frame,
                timeout_seconds=timeout_seconds,
                monotonic=monotonic,
            )
        # Final gate after the receipt and directly before publish. A full
        # stream is not authority to publish if cancellation/deadline changed.
        try:
            if should_cancel is not None and should_cancel():
                raise RGB24TransferCancelled("RGB24 publish cancelled")
        except RGB24TransferError:
            raise
        except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
            raise RGB24TransferError("RGB24 pre-publication check failed") from None
        if timeout_seconds is not None:
            reading = safe_clock()
            if reading < started or reading - started > timeout_seconds:
                raise RGB24TransferTimeout("RGB24 publish time budget exceeded")
        try:
            stage.publish(receipt)
        except (OSError, ValueError, RuntimeError, TypeError):
            raise RGB24TransferError("RGB24 staged publish failed") from None
        published = True
        return receipt
    finally:
        if not published:
            # Preserve the original failure or cancellation.
            with suppress(Exception):
                stage.discard()
