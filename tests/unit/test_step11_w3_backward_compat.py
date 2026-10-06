from pathlib import Path

from ai_ngerti_geopolitik.domain import ClipProperties
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def test_old_schema_v1_fixture_loads_with_default_w3_properties() -> None:
    fixture = Path("tests/fixtures/step11_schema_v1_minimal.angproj")
    state = JsonProjectRepository().load(fixture)
    for track in state.tracks:
        for clip in track.clips:
            assert clip.properties == ClipProperties()
