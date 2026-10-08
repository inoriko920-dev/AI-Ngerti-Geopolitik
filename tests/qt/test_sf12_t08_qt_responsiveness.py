"""T08 Qt UI event loop remains responsive while export background thread blocks."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from PySide6.QtCore import QTimer

from ai_ngerti_geopolitik.application.export_jobs import ExportJobService, ExportJobState
from ai_ngerti_geopolitik.application.export_postflight import PostflightReceipt
from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.ports import ExportResult
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.export_job_adapters import AtomicExportPublisher


class FakePostflight:
    def verify(self, stage_path, request, state, result, cancellation):
        return PostflightReceipt.capture(stage_path, result.duration_frames)


class BlockedRender:
    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()

    def render(self, state, request, *, stage_path, cancellation):
        self.entered.set()
        while not self.release.wait(timeout=0.01):
            if cancellation.cancelled:
                raise RuntimeError("cancelled")
        stage_path.write_bytes(b"Qt responsiveness-only placeholder")
        return ExportResult(state.revision, stage_path, 30, 1920, 1080, 30)


def test_qtimer_continues_during_blocked_render_and_close(qtbot, tmp_path: Path) -> None:
    state = ProjectState.create("P-QT", "T08 Qt")
    request = ExportRequest.for_project(
        state,
        request_id="T08-QT",
        session_id="QT-session",
        output_path=tmp_path / "must-not-create.mp4",
    )
    engine = BlockedRender()
    with ExportJobService(engine, AtomicExportPublisher(), postflight=FakePostflight()) as jobs:
        counter = [0]
        poll_states = []
        timer = QTimer()
        timer.setInterval(10)

        def tick() -> None:
            counter[0] += 1
            poll_states.append(
                jobs.snapshot(request.request_id, state=state, session_id="QT-session").status
            )

        jobs.submit(state, request, session_id="QT-session")
        assert engine.entered.wait(timeout=4)
        timer.timeout.connect(tick)
        timer.start()
        qtbot.waitUntil(lambda: counter[0] >= 8, timeout=4000)
        assert ExportJobState.RUNNING in poll_states
        begin = time.monotonic()
        jobs.shutdown(wait=False)
        assert time.monotonic() - begin < 0.5
        timer.stop()
        engine.release.set()
        assert not request.output_path.exists()
