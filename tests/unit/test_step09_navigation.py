import pytest

from ai_ngerti_geopolitik.presentation.navigation import ROUTES, UiRoute, parse_route


def test_representative_step09_routes_match_frozen_aavc_anchor_set() -> None:
    assert {route.value for route in UiRoute} == {
        "UI-002",
        "UI-003",
        "UI-010",
        "UI-013",
        "UI-014",
        "UI-027",
        "UI-035",
        "UI-041",
    }
    assert len(ROUTES) == 8
    assert parse_route("ui-027") is UiRoute.SUBTITLE_EDITOR


def test_unknown_ui_route_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown UI route"):
        parse_route("UI-999")
