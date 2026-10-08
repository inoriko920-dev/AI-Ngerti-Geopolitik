"""W8-010 runtime binding for frozen UI-039, UI-040 and UI-041.

Bootstrap owns concrete adapters and Qt event timing; application services own
project truth, typed validation, verified relink and crash recovery.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.project_jobs import (
    ProjectJobState,
    ReadOnlyProjectJobs,
)
from ai_ngerti_geopolitik.application.project_session import (
    ProjectSession,
)
from ai_ngerti_geopolitik.application.recovery import (
    CrashMarker,
    RecoveryChoice,
    RecoveryManager,
    RecoveryOffer,
)
from ai_ngerti_geopolitik.application.relink_scan import (
    RelinkScanJobService,
    RelinkScanSnapshot,
    ScanState,
)
from ai_ngerti_geopolitik.application.ui_intents import (
    UiIntent,
    UiIntentSink,
    UiIntentType,
)
from ai_ngerti_geopolitik.application.validation import (
    RealMediaIntegrityRule,
    ValidationResult,
    ValidationService,
)
from ai_ngerti_geopolitik.infrastructure.crash_marker import FileCrashMarkerStore
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.media_status import LocalMediaAvailability
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.relink_scan import LocalRelinkDirectoryScanner
from ai_ngerti_geopolitik.presentation.asset_scan import asset_scan_projection
from ai_ngerti_geopolitik.presentation.main_window import MainWindow
from ai_ngerti_geopolitik.presentation.navigation import UiRoute
from ai_ngerti_geopolitik.presentation.recovery import recovery_projection
from ai_ngerti_geopolitik.presentation.validation_center import project_validation_center


class _DeferredProbe:
    """Resolve FFprobe only inside a real worker, never when starting the UI."""

    def probe(self, path: Path) -> ProbeResult:
        return FfprobeMediaProbe().probe(path)


class W8IntentRouter:
    """Stable sink injected when the window and nested editor tabs are created."""

    def __init__(self) -> None:
        self.delegate: UiIntentSink | None = None

    def __call__(self, intent: UiIntent) -> None:
        if self.delegate is not None:
            self.delegate(intent)


class W8RuntimeController:
    """One GUI-thread owner for UI lifecycle; never probes or scans on the UI thread."""

    def __init__(
        self,
        window: MainWindow,
        *,
        session: ProjectSession | None = None,
        recovery: RecoveryManager | None = None,
        validation: ValidationService | None = None,
        relink: RelinkScanJobService | None = None,
        timer_enabled: bool = True,
    ) -> None:
        from PySide6.QtCore import QTimer

        self.window = window
        self.repository = JsonProjectRepository()
        self.session = session or ProjectSession(self.repository)
        self.recovery = recovery or RecoveryManager(
            self.session.repository,
            self.session.autosave_catalog,
            FileCrashMarkerStore(),
        )
        probe = _DeferredProbe()
        self.validation = validation or ValidationService(
            (RealMediaIntegrityRule(LocalMediaIntegrityInspector(probe)),)
        )
        self.relink = relink or RelinkScanJobService(LocalRelinkDirectoryScanner(), probe)
        self.validation_jobs: ReadOnlyProjectJobs[ValidationResult] = ReadOnlyProjectJobs()
        self.recovery_worker = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="ang-w8-recovery"
        )
        self.session_id = uuid4().hex
        self.validation_job_id: str | None = None
        self.scan_job_id: str | None = None
        self.last_scan_signature: tuple[object, ...] | None = None
        self.offer: RecoveryOffer | None = None
        self.recovery_future: Future[RecoveryOffer] | None = None
        self.recovery_path: Path | None = None
        self.active_marker: CrashMarker | None = None
        self.last_error = ""
        self._closed = False
        self.timer = QTimer(self.window.window)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.poll)
        if timer_enabled:
            self.timer.start()

    def _notify(self, message: str) -> None:
        self.last_error = message
        self.window.window.statusBar().showMessage(message, 7500)

    def _finish_current_session(self) -> bool:
        if not self.session.is_open:
            return True
        if self.session.dirty:
            self._notify("Project belum disimpan. Simpan sebelum membuka project lain.")
            return False
        if self.active_marker is not None and self.session.current_path is not None:
            self.recovery.close_clean(self.session, self.session.current_path, self.active_marker)
        else:
            self.session.close()
        self.active_marker = None
        self.session_id = uuid4().hex
        return True

    def request_open(self, source: Path) -> None:
        """Asynchronous catalog inspection; never perform disk probing on GUI thread."""
        if self._closed or self.recovery_future is not None:
            return
        # Do not discard a valid open project until the candidate has passed
        # asynchronous recovery inspection. A corrupt/missing destination is
        # not a reason to close the currently active project.
        if self.session.is_open and self.session.dirty:
            self._notify("Project belum disimpan. Simpan sebelum membuka project lain.")
            return
        candidate = source.resolve()
        if self.session.is_open and self.session.current_path == candidate:
            self._notify("Project ini sudah terbuka.")
            return
        self.offer = None
        self.recovery_path = candidate
        self.recovery_future = self.recovery_worker.submit(
            self.recovery.inspect, self.recovery_path
        )
        self._notify("Memeriksa autosave dan status pemulihan project…")

    def _cancel_project_jobs(self) -> None:
        if self.validation_job_id is not None:
            self.validation_jobs.cancel(self.validation_job_id)
            self.validation_job_id = None
        if self.scan_job_id is not None:
            self.relink.cancel(self.scan_job_id)
            self.scan_job_id = None
        self.last_scan_signature = None

    def _decide(self, choice: RecoveryChoice, selected: Path | None = None) -> None:
        if self.offer is None:
            self._notify("Pilihan pemulihan tidak tersedia.")
            return
        if choice is RecoveryChoice.IGNORE:
            self.offer = None
            self.window._close_active_dialog()
            return
        if self.session.is_open and self.session.dirty:
            self._notify("Project belum disimpan. Simpan sebelum membuka project lain.")
            return

        # Stage on a temporary session: RecoveryManager verifies the latest
        # source/snapshot and starts its marker BEFORE the active editor changes.
        # This is not a second live project store; it becomes the sole session
        # only after the previous session has been closed successfully.
        candidate_session = ProjectSession(
            self.session.repository, autosave_catalog=self.session.autosave_catalog
        )
        offer = self.offer
        try:
            decision = self.recovery.decide(
                offer, choice, candidate_session, selected_path=selected
            )
        except (OSError, RuntimeError, ValueError):
            self._notify("Pemulihan gagal atau sudah usang. Buka project kembali.")
            return

        try:
            finished = self._finish_current_session()
        except (OSError, RuntimeError, ValueError):
            finished = False
        if not finished:
            # Candidate never becomes the active project. Make a best-effort
            # clean marker for a stage that was never accepted into the editor.
            if decision.active_marker is not None:
                with suppress(OSError, RuntimeError, ValueError):
                    self.recovery.close_clean(
                        candidate_session,
                        offer.source,
                        decision.active_marker,
                        discard_unsaved=True,
                    )
            self._notify("Tidak dapat menutup project sebelumnya. Project baru belum dibuka.")
            return

        self._cancel_project_jobs()
        self.session = candidate_session
        self.active_marker = decision.active_marker
        self.offer = None
        self.session_id = uuid4().hex
        # The successful OPEN/RECOVER action must activate the existing editor
        # route. Previously the project loaded but Home remained visible.
        self.window.show_route(UiRoute.EDITOR)
        self._notify("Project dibuka. Periksa media dan simpan perubahan secara manual.")
        self.request_validation()

    def request_validation(self) -> None:
        if not self.session.is_open or self._closed:
            self._notify("Buka project terlebih dahulu untuk memulai validasi.")
            return
        if self.validation_job_id is not None:
            self.validation_jobs.cancel(self.validation_job_id)
        snapshot = self.session.state
        self.validation_job_id = self.validation_jobs.submit(
            snapshot,
            session_id=self.session_id,
            work=lambda: self.validation.validate(snapshot),
        ).job_id
        self._notify("Memvalidasi media project di worker…")

    def show_asset_scan(self) -> None:
        """Opens UI-040 with an inert empty projection until a directory is selected."""
        from ai_ngerti_geopolitik.application.project_jobs import ProjectJobToken

        if not self.session.is_open:
            self._notify("Buka project sebelum memindai aset.")
            return
        self._cancel_scan_only()
        empty = RelinkScanSnapshot(
            "",
            ProjectJobToken.capture(self.session.state, self.session_id),
            ScanState.SUCCESS,
            0,
            (),
        )
        self.window.present_asset_scan(asset_scan_projection(empty))

    def _cancel_scan_only(self) -> None:
        if self.scan_job_id is not None:
            self.relink.cancel(self.scan_job_id)
            self.scan_job_id = None
        self.last_scan_signature = None

    def start_scan(self, folder: Path) -> None:
        if not self.session.is_open or self._closed:
            return
        self._cancel_scan_only()
        # Existing canonical asset availability is refreshed through CommandBus.
        from ai_ngerti_geopolitik.application.media_status import MediaStatusService

        MediaStatusService(LocalMediaAvailability()).refresh(self.session)
        try:
            scan = self.relink.submit(self.session.state, folder, session_id=self.session_id)
        except (OSError, RuntimeError, ValueError):
            self._notify("Folder scan tidak tersedia atau tidak dapat diakses.")
            return
        self.scan_job_id = scan.job_id
        self.window.present_asset_scan(asset_scan_projection(scan))

    def _apply_scan(self, payload: tuple[tuple[str, str], ...]) -> None:
        if self.scan_job_id is None or not self.session.is_open:
            self._notify("Tidak ada hasil scan yang aktif.")
            return
        try:
            updated = self.relink.apply_selected(
                self.scan_job_id,
                self.session,
                session_id=self.session_id,
                selections=tuple((asset_id, Path(path)) for asset_id, path in payload),
            )
        except (OSError, RuntimeError, ValueError):
            self._notify("Kandidat sudah usang/tidak cocok. Scan ulang sebelum relink.")
            return
        self._cancel_scan_only()
        self._notify(f"Media terverifikasi diterapkan pada revisi {updated.revision}.")
        self.request_validation()

    def handle(self, intent: UiIntent) -> None:
        if self._closed:
            return
        kind = intent.kind
        data = dict(intent.payload)
        if kind is UiIntentType.NEW_PROJECT:
            if data.get("action") == "continue_wizard":
                scene_docx = data.get("path", "").strip()
                if not scene_docx:
                    self._notify("Pilih Scene DOCX sebelum melanjutkan.")
                elif Path(scene_docx).suffix.lower() != ".docx" or not Path(scene_docx).is_file():
                    self._notify("Scene DOCX tidak tersedia. Pilih file DOCX yang dapat dibuka.")
                else:
                    # DOCX Scene + Asset-ID ingestion has not been implemented
                    # in the live W8 controller. Do not silently invent a
                    # ProjectSession or navigate to an empty editor.
                    self._notify("Impor Scene DOCX belum terhubung. Project belum dibuat.")
        elif kind is UiIntentType.OPEN_PROJECT:
            filename = data.get("path", "")
            if not filename:
                from PySide6.QtWidgets import QFileDialog

                filename, _ = QFileDialog.getOpenFileName(
                    self.window.window, "Buka Project", "", "Project (*.angproj)"
                )
            if filename:
                self.request_open(Path(filename))
        elif kind is UiIntentType.RECOVERY_OPEN_SOURCE:
            self._decide(RecoveryChoice.OPEN_SOURCE)
        elif kind is UiIntentType.RECOVERY_RESTORE_SNAPSHOT:
            self._decide(RecoveryChoice.RECOVER_SNAPSHOT, Path(data.get("snapshot", "")))
        elif kind is UiIntentType.RECOVERY_IGNORE:
            self._decide(RecoveryChoice.IGNORE)
        elif kind is UiIntentType.OPEN_VALIDATION:
            if data.get("action") == "RELINK_MEDIA":
                self.show_asset_scan()
            else:
                self.request_validation()
        elif kind is UiIntentType.ASSET_SCAN_START:
            folder = data.get("root", "")
            if not folder:
                from PySide6.QtWidgets import QFileDialog

                folder = QFileDialog.getExistingDirectory(self.window.window, "Pilih Folder Media")
            if folder:
                self.start_scan(Path(folder))
        elif kind is UiIntentType.ASSET_SCAN_CANCEL:
            self._cancel_scan_only()
            self._notify("Scan media dibatalkan.")
            self.show_asset_scan()
        elif kind is UiIntentType.ASSET_SCAN_APPLY:
            self._apply_scan(intent.payload)
        elif kind is UiIntentType.SAVE_PROJECT and self.session.is_open:
            try:
                self.session.save()
                self._notify("Project berhasil disimpan.")
            except (OSError, RuntimeError, ValueError):
                self._notify("Project belum tersimpan. Periksa folder dan ulangi Simpan.")

    def poll(self) -> None:
        """Qt GUI-thread tick consuming read-only job results; no blocking work."""
        if self._closed:
            return
        if self.recovery_future is not None and self.recovery_future.done():
            future = self.recovery_future
            self.recovery_future = None
            try:
                offer = future.result()
            except (OSError, RuntimeError, ValueError):
                self._notify("Tidak dapat memeriksa project atau autosave.")
            else:
                if self.recovery_path == offer.source:
                    self.offer = offer
                    if offer.can_recover:
                        self.window.present_recovery(recovery_projection(offer))
                    else:
                        self._decide(RecoveryChoice.OPEN_SOURCE)
        if self.validation_job_id is not None:
            snapshot = self.validation_jobs.snapshot(
                self.validation_job_id,
                state=self.session.state if self.session.is_open else None,
                session_id=self.session_id,
            )
            if snapshot.state not in {ProjectJobState.QUEUED, ProjectJobState.RUNNING}:
                self.validation_job_id = None
                if snapshot.state is ProjectJobState.SUCCESS and snapshot.result is not None:
                    projection = project_validation_center(snapshot.result, self.session.state)
                    self.window.present_validation(projection)
                elif snapshot.state is ProjectJobState.FAILED:
                    self._notify("Validasi gagal. Jalankan Validasi Ulang.")
        if self.scan_job_id is not None:
            result = self.relink.snapshot(
                self.scan_job_id,
                state=self.session.state if self.session.is_open else None,
                session_id=self.session_id,
            )
            signature = (result.state, result.scanned_files, len(result.candidates), result.applied)
            if signature != self.last_scan_signature:
                self.last_scan_signature = signature
                self.window.present_asset_scan(asset_scan_projection(result))
            if result.state in {ScanState.STALE, ScanState.CANCELLED, ScanState.FAILED}:
                self.scan_job_id = None

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.timer.stop()
        self._cancel_project_jobs()
        self.validation_jobs.shutdown()
        self.relink.shutdown()
        self.recovery_worker.shutdown(wait=False, cancel_futures=True)
        # Never pretend clean shutdown when unsaved work still exists.
        if self.session.is_open and not self.session.dirty:
            with suppress(OSError, RuntimeError, ValueError):
                self._finish_current_session()
