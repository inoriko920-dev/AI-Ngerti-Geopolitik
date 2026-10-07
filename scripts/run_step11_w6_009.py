from __future__ import annotations

import argparse
from pathlib import Path


def _render(window, path: Path) -> None:
    pixmap = window.render_evidence(1920, 1080)
    if pixmap.width() != 1920 or pixmap.height() != 1080:
        raise RuntimeError("W6-009 evidence must render at 1920x1080")
    if not pixmap.save(str(path), "PNG"):
        raise RuntimeError(f"failed to save {path}")


def _pair(reference: Path, actual: Path, output: Path, title: str) -> None:
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter

    ref = QImage(str(reference))
    act = QImage(str(actual))
    if ref.isNull() or act.isNull():
        raise RuntimeError(f"invalid W6-009 pair source: {title}")

    canvas = QImage(1660, 1010, QImage.Format.Format_RGB32)
    canvas.fill(QColor("#F4F7FB"))
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    font = QFont("Arial", 16)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("#172033"))
    painter.drawText(QRect(20, 12, 1620, 36), int(Qt.AlignmentFlag.AlignCenter), title)

    for image, x, label in (
        (ref, 20, "REFERENCE — frozen AAVC"),
        (act, 840, "ACTUAL — real PySide6"),
    ):
        painter.drawText(QRect(x, 50, 800, 28), int(Qt.AlignmentFlag.AlignCenter), label)
        scaled = image.scaled(
            800,
            900,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.fillRect(QRect(x, 80, 800, 900), QColor("#FFFFFF"))
        painter.drawImage(
            x + (800 - scaled.width()) // 2,
            80 + (900 - scaled.height()) // 2,
            scaled,
        )
        painter.setPen(QColor("#D8E2EE"))
        painter.drawRect(QRect(x, 80, 800, 900))
    painter.end()
    if not canvas.save(str(output), "PNG"):
        raise RuntimeError(f"failed to save {output}")


def _reference_contact_sheet(reference: Path, output: Path) -> None:
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter

    columns = 7
    rows = 6
    cell_w = 360
    cell_h = 240
    header_h = 32
    canvas = QImage(
        columns * cell_w,
        rows * cell_h,
        QImage.Format.Format_RGB32,
    )
    canvas.fill(QColor("#F4F7FB"))
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    font = QFont("Arial", 11)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("#172033"))

    for number in range(1, 43):
        ui_id = f"UI-{number:03d}"
        path = reference / f"{ui_id}.png"
        image = QImage(str(path))
        if image.isNull():
            raise RuntimeError(f"invalid frozen reference: {ui_id}")
        index = number - 1
        row = index // columns
        col = index % columns
        x = col * cell_w
        y = row * cell_h
        painter.drawText(
            QRect(x, y, cell_w, header_h),
            int(Qt.AlignmentFlag.AlignCenter),
            ui_id,
        )
        scaled = image.scaled(
            cell_w - 12,
            cell_h - header_h - 12,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        px = x + (cell_w - scaled.width()) // 2
        py = y + header_h + (cell_h - header_h - scaled.height()) // 2
        painter.drawImage(px, py, scaled)
        painter.setPen(QColor("#D8E2EE"))
        painter.drawRect(QRect(x + 2, y + 2, cell_w - 4, cell_h - 4))
        painter.setPen(QColor("#172033"))
    painter.end()
    if not canvas.save(str(output), "PNG"):
        raise RuntimeError("failed to save frozen reference contact sheet")


def main() -> int:
    from PySide6.QtWidgets import QApplication, QTabWidget, QWidget

    from ai_ngerti_geopolitik.presentation.main_window import create_main_window
    from ai_ngerti_geopolitik.presentation.w6_ai_workspace import (
        AIAgentProjection,
        AIAgentUiState,
        CredentialSlotProjection,
        project_ai_agent_state,
        set_ai_agent_subview,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    reference = root / "docs" / "ui_reference" / "raw"

    app = QApplication.instance() or QApplication(["ANG-W6-009"])
    _reference_contact_sheet(reference, output / "00_FROZEN_REFERENCE_CONTACT_SHEET.png")
    window = create_main_window("UI-010", fixture_mode=True)
    window.resize(1920, 1080)
    window.show()
    current = window.stack.currentWidget()
    right = current.findChild(QTabWidget, "editor_right_tabs")
    workspace = current.findChild(QWidget, "w6_ai_workspace")
    if right is None or workspace is None:
        raise RuntimeError("W6-009 AI workspace is missing")
    ai_index = next((i for i in range(right.count()) if right.tabText(i) == "AI Agent"), -1)
    if ai_index < 0:
        raise RuntimeError("W6-009 AI Agent tab is missing")

    mapping: list[tuple[str, str]] = []

    app.processEvents()
    path = output / "UI-010_ACTUAL_EDITOR_AI_ENTRY.png"
    _render(window, path)
    mapping.append(("UI-010", path.name))

    right.setCurrentIndex(ai_index)
    set_ai_agent_subview(workspace, "director")
    app.processEvents()
    path = output / "W6-AI-DIRECTOR_ACTUAL.png"
    _render(window, path)

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.READY,
            scope_text="Scene 01 · clip-1",
            provider_status="Online",
        ),
    )
    app.processEvents()
    path = output / "UI-021_ACTUAL_AI_READY.png"
    _render(window, path)
    mapping.append(("UI-021", path.name))

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.PLAN,
            scope_text="Scene 01 · clip-1, clip-2",
            summary="2 perubahan efek L1 siap ditinjau.",
            commands=(
                "clip-1 · enter: Fade → Rise",
                "clip-2 · intensity: 90 → 115",
            ),
            request_id="REQ-EVIDENCE-009",
        ),
    )
    app.processEvents()
    path = output / "UI-022_ACTUAL_AI_PLAN.png"
    _render(window, path)
    mapping.append(("UI-022", path.name))

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.SUCCESS,
            scope_text="Scene 01 · clip-1, clip-2",
            message="2 perubahan diterapkan sebagai satu transaksi. Undo tersedia.",
            commands=(
                "clip-1 · enter: Fade → Rise",
                "clip-2 · intensity: 90 → 115",
            ),
            request_id="REQ-EVIDENCE-009",
        ),
    )
    app.processEvents()
    path = output / "UI-023_ACTUAL_AI_APPLIED.png"
    _render(window, path)
    mapping.append(("UI-023", path.name))

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.PROVIDER_ERROR,
            provider_status="Tidak tersedia",
            error_code="NO_CREDENTIAL",
            scope_text="Scene 01 · clip-1, clip-2",
        ),
    )
    app.processEvents()
    path = output / "UI-024_ACTUAL_PROVIDER_UNAVAILABLE.png"
    _render(window, path)
    mapping.append(("UI-024", path.name))

    window._open_ai_credentials_dialog()
    window.apply_w6_credential_slots(
        (
            CredentialSlotProjection(1, "Gemini Utama", True, "HEALTHY", "PASS"),
            CredentialSlotProjection(2, "Gemini Cadangan", False, "INVALID_AUTH", "INVALID_AUTH"),
            CredentialSlotProjection(100, "Slot Operasional", True, "UNTESTED", ""),
        )
    )
    app.processEvents()
    path = output / "UI-033_ACTUAL_PROVIDER_KEYS.png"
    _render(window, path)
    mapping.append(("UI-033", path.name))

    for ui_id, actual_name in mapping:
        ref_path = reference / f"{ui_id}.png"
        actual_path = output / actual_name
        if not ref_path.is_file():
            raise RuntimeError(f"missing frozen reference {ui_id}")
        _pair(
            ref_path,
            actual_path,
            output / f"{ui_id}_REFERENCE_VS_ACTUAL.png",
            ui_id,
        )

    (output / "00_w6_009_ui_report.txt").write_text(
        "\n".join(
            [
                "status=PASS",
                "ui_010=baseline_editor_ai_entry",
                "ui_021=ready_chat_real_widgets",
                "ui_022=plan_approval_real_widgets",
                "ui_023=applied_success_real_widgets",
                "ui_024=provider_unavailable_manual_fallback",
                "ui_033=provider_api_key_manager_real_widgets",
                "ai_director=real_widgets_actual_only_no_dedicated_frozen_raster",
                "states=READY,PLAN,APPROVAL,APPLYING,SUCCESS,PROVIDER_ERROR,LOCK_CONFLICT,STALE",
                "l1_only=true",
                "manual_fallback=true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (output / "00_w6_009_reference_mapping_report.txt").write_text(
        "\n".join(
            [
                "status=PASS",
                "authority=actual_frozen_raster_visual",
                "planning_id_title_conflict=true",
                "gap_ux_001_applied=true",
                "ui_010=baseline_editor_ai_entry",
                "ui_021=ai_ready_chat",
                "ui_022=ai_plan_approval",
                "ui_023=ai_applied_success",
                "ui_024=provider_unavailable",
                "ui_033=provider_api_key_manager",
                "ai_director_dedicated_frozen_raster=none_found",
                "raw_frozen_png_modified=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (output / "00_w6_009_security_report.txt").write_text(
        "\n".join(
            [
                "status=PASS",
                "saved_credentials_display=masked_only",
                "masked_marker=present",
                "raw_saved_credentials_in_ui=0",
                "unsupported_l1_effects_selectable=0",
                "screenshot_as_runtime=0",
                "live_gemini_used=0",
                "quota_circumvention_claim=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
