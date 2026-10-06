from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import (
    RecordingIntentSink,
    UiIntent,
    UiIntentSink,
    UiIntentType,
)
from ai_ngerti_geopolitik.presentation.design_tokens import METRICS, app_stylesheet
from ai_ngerti_geopolitik.presentation.navigation import UiRoute, parse_route


class MainWindow:
    """Real PySide6 app shell for SF-STEP 09."""

    def __init__(
        self,
        initial_state: str = "UI-002",
        *,
        fixture_mode: bool = False,
        intent_sink: UiIntentSink | None = None,
        media_path_provider: Callable[[], str | None] | None = None,
    ) -> None:
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import QMainWindow, QStackedWidget, QToolBar

        self.fixture_mode = fixture_mode
        self.intent_recorder = RecordingIntentSink()
        self.intent_sink = intent_sink or self.intent_recorder
        self.media_path_provider = media_path_provider
        self.window = QMainWindow()
        self.window.setObjectName("ANGMainWindow")
        self.window.setWindowTitle("AI Ngerti Geopolitik")
        self.window.resize(1600, 900)
        self.window.setMinimumSize(1280, 720)
        from PySide6.QtGui import QFontDatabase

        families = set(QFontDatabase.families())
        font_family = (
            "Segoe UI"
            if "Segoe UI" in families
            else ("Arial" if "Arial" in families else self.window.font().family())
        )
        self.window.setStyleSheet(app_stylesheet(font_family))
        self.stack = QStackedWidget()
        self.stack.setObjectName("stack_main_routes")
        self.window.setCentralWidget(self.stack)
        self._route_widgets: dict[UiRoute, Any] = {}
        self._toolbar: Any | None = None
        self._active_dialog: Any | None = None
        self._build_menu(QAction)
        self._build_toolbar(QToolBar, QAction)
        self._build_pages()
        self.show_route(parse_route(initial_state))

    def _emit(self, kind: UiIntentType, **payload: str) -> None:
        self.intent_sink(UiIntent(kind, tuple(sorted(payload.items()))))

    def _build_menu(self, action_type: Any) -> None:
        menu_bar = self.window.menuBar()
        menu_bar.setObjectName("menu_bar_main")
        for name in ["File", "Edit", "Proyek", "Tampilan", "Animasi", "AI", "Ekspor", "Bantuan"]:
            menu = menu_bar.addMenu(name)
            menu.setObjectName(f"menu_{name.lower()}")
            if name == "File":
                new_action = action_type("Proyek Baru", self.window)
                new_action.triggered.connect(lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX))
                menu.addAction(new_action)
                open_action = action_type("Buka Proyek", self.window)
                open_action.triggered.connect(lambda: self._emit(UiIntentType.OPEN_PROJECT))
                menu.addAction(open_action)
                menu.addSeparator()
                save_action = action_type("Simpan", self.window)
                save_action.triggered.connect(lambda: self._emit(UiIntentType.SAVE_PROJECT))
                menu.addAction(save_action)
                exit_action = action_type("Keluar", self.window)
                exit_action.triggered.connect(self.window.close)
                menu.addAction(exit_action)
            elif name == "Edit":
                undo = action_type("Undo", self.window)
                undo.triggered.connect(lambda: self._emit(UiIntentType.UNDO))
                redo = action_type("Redo", self.window)
                redo.triggered.connect(lambda: self._emit(UiIntentType.REDO))
                menu.addAction(undo)
                menu.addAction(redo)
            elif name == "Ekspor":
                export = action_type("Ekspor Video", self.window)
                export.triggered.connect(lambda: self.show_route(UiRoute.EXPORT_SETTINGS))
                menu.addAction(export)
            else:
                placeholder = action_type(f"{name} — STEP 09 shell", self.window)
                placeholder.triggered.connect(
                    lambda _checked=False, value=name: self._emit(
                        UiIntentType.SELECT_SCENE,
                        menu=value,
                    )
                )
                menu.addAction(placeholder)

    def _build_toolbar(self, toolbar_type: Any, action_type: Any) -> None:
        from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QSizePolicy, QWidget

        toolbar = toolbar_type("Utama", self.window)
        toolbar.setObjectName("toolbar_main")
        toolbar.setMovable(False)
        toolbar.setFixedHeight(METRICS.toolbar_h)
        items = [
            ("Baru", UiIntentType.NEW_PROJECT),
            ("Buka", UiIntentType.OPEN_PROJECT),
            ("Simpan", UiIntentType.SAVE_PROJECT),
            ("Undo", UiIntentType.UNDO),
            ("Redo", UiIntentType.REDO),
            ("Impor Media", UiIntentType.IMPORT_MEDIA),
            ("Tambah Teks", UiIntentType.ADD_TEXT),
            ("Rekam Narasi", UiIntentType.RECORD_NARRATION),
        ]
        for label, kind in items:
            action = action_type(label, self.window)
            action.setObjectName(f"action_{kind.value}")
            if kind is UiIntentType.NEW_PROJECT:
                action.triggered.connect(lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX))
            elif kind is UiIntentType.IMPORT_MEDIA:
                action.triggered.connect(self._request_import_media)
            else:
                action.triggered.connect(lambda _checked=False, value=kind: self._emit(value))
            toolbar.addAction(action)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Mode Animasi"))
        animation = QComboBox()
        animation.setObjectName("combo_animation_mode")
        animation.addItems(["Auto (AI)", "Random App", "Manual"])
        animation.setMaximumWidth(130)
        toolbar.addWidget(animation)

        validation = QPushButton("✓ Validasi OK")
        validation.setObjectName("btn_open_validation")
        validation.setAccessibleName("Buka Pusat Validasi")
        validation.setStyleSheet(
            "color:#15803D; background:#F0FDF4; border:1px solid #BBF7D0; "
            "border-radius:6px; padding:5px 9px; font-weight:600;"
        )
        validation.clicked.connect(lambda: self.show_route(UiRoute.VALIDATION_CENTER))
        toolbar.addWidget(validation)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        export = QPushButton("Ekspor Video")
        export.setObjectName("btn_export_video")
        export.setAccessibleName("Ekspor Video")
        export.setProperty("primary", True)
        export.clicked.connect(lambda: self.show_route(UiRoute.EXPORT_SETTINGS))
        toolbar.addWidget(export)
        self.window.addToolBar(toolbar)
        self._toolbar = toolbar

    def _request_import_media(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        if self.media_path_provider is not None:
            path = self.media_path_provider()
        else:
            path, _ = QFileDialog.getOpenFileName(
                self.window,
                "Impor Media",
                "",
                "Video (*.mp4 *.mov *.mkv *.avi *.webm);;Semua File (*.*)",
            )
        if path:
            self._emit(UiIntentType.IMPORT_MEDIA, path=path)

    def _build_pages(self) -> None:
        from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
        from ai_ngerti_geopolitik.presentation.home import create_home_screen
        from ai_ngerti_geopolitik.presentation.new_project import create_new_project_screen

        def open_new_project() -> None:
            self._emit(UiIntentType.NEW_PROJECT)
            self.show_route(UiRoute.NEW_PROJECT_DOCX)

        def open_existing_project() -> None:
            self._emit(UiIntentType.OPEN_PROJECT)

        self._route_widgets[UiRoute.HOME] = create_home_screen(
            open_new_project,
            open_existing_project,
        )

        def continue_new_project() -> None:
            self._emit(UiIntentType.NEW_PROJECT, action="continue_wizard")
            self.show_route(UiRoute.EDITOR)

        self._route_widgets[UiRoute.NEW_PROJECT_DOCX] = create_new_project_screen(
            lambda: self.show_route(UiRoute.HOME),
            continue_new_project,
        )
        self._route_widgets[UiRoute.EDITOR] = create_editor_shell("overview", self.intent_sink).root
        self._route_widgets[UiRoute.SCENE_SINGLE] = create_editor_shell(
            "single", self.intent_sink
        ).root
        self._route_widgets[UiRoute.SCENE_DOUBLE] = create_editor_shell(
            "double", self.intent_sink
        ).root
        self._route_widgets[UiRoute.SUBTITLE_EDITOR] = create_editor_shell(
            "subtitle", self.intent_sink
        ).root
        self._route_widgets[UiRoute.EXPORT_SETTINGS] = create_editor_shell(
            "subtitle", self.intent_sink
        ).root
        self._route_widgets[UiRoute.VALIDATION_CENTER] = create_editor_shell(
            "overview", self.intent_sink
        ).root
        for widget in self._route_widgets.values():
            self.stack.addWidget(widget)

    def _close_active_dialog(self) -> None:
        if self._active_dialog is None:
            return
        self._active_dialog.close()
        self._active_dialog.deleteLater()
        self._active_dialog = None

    def show_route(self, route: UiRoute) -> None:
        from ai_ngerti_geopolitik.presentation.dialogs import (
            create_export_dialog,
            create_validation_dialog,
        )

        self._close_active_dialog()
        self.stack.setCurrentWidget(self._route_widgets[route])
        self.window.setProperty("ui_state", route.value)
        editor_chrome = route not in {UiRoute.HOME, UiRoute.NEW_PROJECT_DOCX}
        self.window.menuBar().setVisible(editor_chrome)
        if self._toolbar is not None:
            self._toolbar.setVisible(editor_chrome)
        if route is UiRoute.EXPORT_SETTINGS:
            self._emit(UiIntentType.OPEN_EXPORT)
            dialog = create_export_dialog(self.window, self.intent_sink)
            dialog.setModal(True)
            dialog.show()
            self._active_dialog = dialog
        elif route is UiRoute.VALIDATION_CENTER:
            self._emit(UiIntentType.OPEN_VALIDATION)
            dialog = create_validation_dialog(self.window, self.intent_sink)
            dialog.setModal(False)
            dialog.show()
            self._active_dialog = dialog

    def apply_step10_timeline_projection(self, projection: Any) -> None:
        from PySide6.QtWidgets import QLabel

        current = self.stack.currentWidget()
        blocks = [
            current.findChild(QLabel, f"timeline_video_block_{index}")
            for index in range(1, 5)
        ]
        for block in blocks:
            if block is not None:
                block.setVisible(False)
        for index, clip in enumerate(projection.clips[:4]):
            block = blocks[index]
            if block is None:
                raise RuntimeError(f"STEP 10 timeline block {index + 1} not found")
            block.setText(
                f"{clip.clip_id}  {clip.timeline_start_frame}-{clip.timeline_end_frame}f"
            )
            block.setMinimumWidth(max(90, clip.duration_frames * 2))
            block.setVisible(True)
        self.window.setProperty("step10_project_revision", projection.project_revision)

    def apply_step10_preview(self, result: Any) -> None:
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QLabel

        current = self.stack.currentWidget()
        canvas = current.findChild(QLabel, "preview_canvas")
        if canvas is None:
            raise RuntimeError("STEP 10 preview canvas not found")
        pixmap = QPixmap(str(result.output_path))
        if pixmap.isNull():
            raise RuntimeError(f"STEP 10 preview image invalid: {result.output_path}")
        canvas.setPixmap(pixmap)
        canvas.setProperty("step10_project_revision", result.project_revision)
        canvas.setProperty("step10_timeline_frame", result.timeline_frame)

    def show(self) -> None:
        self.window.show()

    def resize(self, width: int, height: int) -> None:
        self.window.resize(width, height)

    def grab(self) -> Any:
        """Grab the currently displayed native window."""
        return self.window.grab()

    def render_evidence(self, width: int = 1920, height: int = 1080) -> Any:
        """Render deterministic full-size UI evidence without desktop-size clipping."""
        from PySide6.QtCore import QRect, Qt
        from PySide6.QtGui import QColor, QPainter, QPixmap
        from PySide6.QtWidgets import QApplication

        self.window.hide()
        self.window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.window.resize(width, height)
        self.window.ensurePolished()
        self.window.show()
        QApplication.processEvents()

        base = QPixmap(width, height)
        base.fill(QColor("#F4F7FB"))
        self.window.render(base)

        dialog = self._active_dialog
        if dialog is None:
            return base

        dialog.hide()
        dialog.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        dialog.ensurePolished()
        dialog.show()
        QApplication.processEvents()

        dialog_pixmap = QPixmap(dialog.size())
        dialog_pixmap.fill(Qt.GlobalColor.transparent)
        dialog.render(dialog_pixmap)

        result = QPixmap(base)
        painter = QPainter(result)
        route = str(self.window.property("ui_state") or "")
        if route == UiRoute.EXPORT_SETTINGS.value:
            painter.fillRect(QRect(0, 0, width, height), QColor(23, 32, 51, 80))
            x = max(0, (width - dialog_pixmap.width()) // 2)
            y = max(0, (height - dialog_pixmap.height()) // 2)
        elif route == UiRoute.VALIDATION_CENTER.value:
            x = max(0, width - dialog_pixmap.width())
            y = max(0, METRICS.menu_h + METRICS.toolbar_h)
        else:
            x = max(0, (width - dialog_pixmap.width()) // 2)
            y = max(0, (height - dialog_pixmap.height()) // 2)
        painter.drawPixmap(x, y, dialog_pixmap)
        painter.end()
        return result

    def close(self) -> None:
        self._close_active_dialog()
        self.window.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.window, name)


def create_main_window(
    initial_state: str = "UI-002",
    *,
    fixture_mode: bool = False,
    intent_sink: UiIntentSink | None = None,
    media_path_provider: Callable[[], str | None] | None = None,
) -> MainWindow:
    return MainWindow(
        initial_state,
        fixture_mode=fixture_mode,
        intent_sink=intent_sink,
        media_path_provider=media_path_provider,
    )
