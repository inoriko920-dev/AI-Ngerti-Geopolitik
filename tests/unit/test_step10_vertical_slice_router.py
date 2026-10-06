from pathlib import Path

from ai_ngerti_geopolitik.application.ports import ExportResult, PreviewResult, ProbeResult
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.application.vertical_slice import (
    VerticalSliceIntentRouter,
    VerticalSliceSession,
)
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class Probe:
    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(path, 240, 30, 1920, 1080, True, "c" * 64)


class Engine:
    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult:
        return PreviewResult(state.revision, timeline_frame, output_path)

    def export(
        self,
        state: ProjectState,
        output_path: Path,
        cancellation=None,
    ) -> ExportResult:
        return ExportResult(state.revision, output_path, 240, 1920, 1080, 30)


def test_import_ui_intent_crosses_application_command_boundary(tmp_path: Path) -> None:
    session = VerticalSliceSession.create(Probe(), JsonProjectRepository(), Engine())
    router = VerticalSliceIntentRouter(session)
    router(
        UiIntent(
            UiIntentType.IMPORT_MEDIA,
            (("path", str(tmp_path / "fixture.mp4")),),
        )
    )
    assert router.last_result == "A001"
    assert session.state.revision == 1
    assert session.state.asset("A001").width == 1920
