from __future__ import annotations

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
    ) -> None:
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import QMainWindow, QStackedWidget, QToolBar

        self.fixture_mode = fixture_mode
        self.intent_recorder = RecordingIntentSink()
        self.intent_sink = intent_sink or self.intent_recorder
        self.window = QMainWindow()
        self.window.setObjectName("ANGMainWindow")
        self.window.setWindowTitle("AI Ngerti Geopolitik")
        self.window.resize(1600, 900)
        self.window.setMinimumSize(1280, 720)
        self.window.setStyleSheet(app_stylesheet())
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
            else:
                action.triggered.connect(
                    lambda _checked=False, value=kind: self._emit(value)
                )
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

    def _build_pages(self) -> None:
        from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
        from ai_ngerti_geopolitik.presentation.home import create_home_screen
        from ai_ngerti_geopolitik.presentation.new_project import create_new_project_screen

        self._route_widgets[UiRoute.HOME] = create_home_screen(
            lambda: self.show_route(UiRoute.NEW_PROJECT_DOCX),
            lambda: self._emit(UiIntentType.OPEN_PROJECT),
            self.intent_sink,
            fixture_mode=self.fixture_mode,
        )
        self._route_widgets[UiRoute.NEW_PROJECT_DOCX] = create_new_project_screen(
            lambda: self.show_route(UiRoute.HOME),
            lambda: self.show_route(UiRoute.EDITOR),
            self.intent_sink,
            fixture_mode=self.fixture_mode,
        )
        self._route_widgets[UiRoute.EDITOR] = create_editor_shell(
            "overview", self.intent_sink
        ).root
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

    def show(self) -> None:
        self.window.show()

    def resize(self, width: int, height: int) -> None:
        self.window.resize(width, height)

    def grab(self) -> Any:
        from PySide6.QtCore import QPoint, QRect
        from PySide6.QtGui import QColor, QPainter, QPixmap

        base = self.window.grab()
        dialog = self._active_dialog
        if dialog is None or not dialog.isVisible():
            return base

        dialog_grab = dialog.grab()
        result = QPixmap(base)
        painter = QPainter(result)
        route = str(self.window.property("ui_state") or "")
        if route == UiRoute.EXPORT_SETTINGS.value:
            painter.fillRect(
                QRect(0, 0, result.width(), result.height()),
                QColor(23, 32, 51, 80),
            )
            x = max(0, (result.width() - dialog_grab.width()) // 2)
            y = max(0, (result.height() - dialog_grab.height()) // 2)
        elif route == UiRoute.VALIDATION_CENTER.value:
            x = max(0, result.width() - dialog_grab.width())
            y = max(0, METRICS.menu_h + METRICS.toolbar_h)
        else:
            global_pos = dialog.mapToGlobal(QPoint(0, 0))
            window_global = self.window.mapToGlobal(QPoint(0, 0))
            x = global_pos.x() - window_global.x()
            y = global_pos.y() - window_global.y()
        painter.drawPixmap(x, y, dialog_grab)
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
) -> MainWindow:
    return MainWindow(initial_state, fixture_mode=fixture_mode, intent_sink=intent_sink)
