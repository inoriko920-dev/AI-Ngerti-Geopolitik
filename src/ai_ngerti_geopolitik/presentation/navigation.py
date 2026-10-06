"""Representative SF-STEP 09 route catalog mapped to frozen AAVC UI IDs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UiRoute(StrEnum):
    HOME = "UI-002"
    NEW_PROJECT_DOCX = "UI-003"
    EDITOR = "UI-010"
    SCENE_SINGLE = "UI-013"
    SCENE_DOUBLE = "UI-014"
    SUBTITLE_EDITOR = "UI-027"
    EXPORT_SETTINGS = "UI-035"
    VALIDATION_CENTER = "UI-041"


@dataclass(frozen=True, slots=True)
class RouteDefinition:
    ui_id: str
    name: str
    family: str


ROUTES: dict[UiRoute, RouteDefinition] = {
    UiRoute.HOME: RouteDefinition("UI-002", "Beranda / Proyek Terbaru", "home"),
    UiRoute.NEW_PROJECT_DOCX: RouteDefinition("UI-003", "Wizard — Scene DOCX", "wizard"),
    UiRoute.EDITOR: RouteDefinition("UI-010", "Editor Utama — Overview", "editor"),
    UiRoute.SCENE_SINGLE: RouteDefinition("UI-013", "Editor — Asset SINGLE", "editor"),
    UiRoute.SCENE_DOUBLE: RouteDefinition("UI-014", "Editor — Scene DOUBLE", "editor"),
    UiRoute.SUBTITLE_EDITOR: RouteDefinition("UI-027", "Subtitle — Teks & Timing", "editor"),
    UiRoute.EXPORT_SETTINGS: RouteDefinition("UI-035", "Ekspor Video", "dialog"),
    UiRoute.VALIDATION_CENTER: RouteDefinition("UI-041", "Pusat Error / Validasi", "drawer"),
}


def parse_route(value: str) -> UiRoute:
    try:
        return UiRoute(value.upper())
    except ValueError as exc:
        valid = ", ".join(route.value for route in UiRoute)
        raise ValueError(f"Unknown UI route {value!r}. Valid: {valid}") from exc
