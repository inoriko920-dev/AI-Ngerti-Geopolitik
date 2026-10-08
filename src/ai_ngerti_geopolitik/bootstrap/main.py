from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

FOUNDATION_MESSAGE = (
    "AI Ngerti Geopolitik foundation ready; full product features are not implemented "
    "in SF-STEP 09."
)
FOUNDATION_SMOKE_TOKEN = "ANG_FOUNDATION_SMOKE_OK"
UI_SMOKE_TOKEN = "ANG_S09_UI_SMOKE_OK"


def _arg_value(args: list[str], flag: str, default: str | None = None) -> str | None:
    if flag not in args:
        return default
    index = args.index(flag)
    if index + 1 >= len(args):
        raise ValueError(f"{flag} requires a value")
    return args[index + 1]


def _write_marker(path_value: str | None, token: str) -> None:
    if not path_value:
        return
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(token, encoding="utf-8")


def run(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        print(FOUNDATION_MESSAGE)
        return 0

    args = list(argv)
    if "--foundation-smoke" in args:
        _write_marker(_arg_value(args, "--foundation-smoke-file"), FOUNDATION_SMOKE_TOKEN)
        print(FOUNDATION_SMOKE_TOKEN)
        print(FOUNDATION_MESSAGE)
        return 0

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QApplication

        from ai_ngerti_geopolitik.presentation.main_window import create_main_window
    except ModuleNotFoundError as exc:
        print(f"Qt runtime belum terpasang: {exc}", file=sys.stderr)
        return 2

    state = _arg_value(args, "--ui-state", "UI-002") or "UI-002"
    capture_path = _arg_value(args, "--capture-path")
    smoke_path = _arg_value(args, "--ui-smoke-file")
    fixture_mode = "--ui-test-mode" in args

    app = QApplication(["AI Ngerti Geopolitik"])
    app.setFont(QFont("Segoe UI", 10))
    # Keep visual/UI smoke runs deterministic; attach live W8 only in product mode.
    live_w8 = not (fixture_mode or capture_path or smoke_path)
    controller = None
    if live_w8:
        from ai_ngerti_geopolitik.bootstrap.w8_controller import (
            W8IntentRouter,
            W8RuntimeController,
        )

        router = W8IntentRouter()
        window = create_main_window(state, fixture_mode=False, intent_sink=router)
        controller = W8RuntimeController(window)
        router.delegate = controller.handle
        app.aboutToQuit.connect(controller.shutdown)
    else:
        window = create_main_window(state, fixture_mode=fixture_mode)
    if capture_path:
        window.resize(1920, 1080)
    window.show()

    if smoke_path:

        def finish_smoke() -> None:
            _write_marker(smoke_path, UI_SMOKE_TOKEN)
            print(UI_SMOKE_TOKEN)
            app.quit()

        QTimer.singleShot(700, finish_smoke)
    elif capture_path:
        target = Path(capture_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        def capture() -> None:
            pixmap = window.render_evidence(1920, 1080)
            if not pixmap.save(str(target), "PNG"):
                print(f"Gagal menyimpan screenshot: {target}", file=sys.stderr)
                app.exit(3)
                return
            print(f"{target} | logical evidence=1920x1080")
            app.quit()

        QTimer.singleShot(900, capture)

    return int(app.exec())
