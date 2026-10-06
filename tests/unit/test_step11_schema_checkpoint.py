def test_schema_v1_checkpoint_fixture_loads() -> None:
    import ai_ngerti_geopolitik.infrastructure.persistence as persistence

    fixture = persistence.Path(__file__).parents[1] / "fixtures" / "step11_schema_v1_minimal.angproj"
    state = persistence.JsonProjectRepository().load(fixture)
    assert state.schema_version == 1
    assert state.project_id == "ANG-S11-SCHEMA-V1"
    assert state.semantic_hash()


def test_future_schema_is_rejected(tmp_path: object) -> None:
    import ai_ngerti_geopolitik.infrastructure.persistence as persistence

    fixture = persistence.Path(__file__).parents[1] / "fixtures" / "step11_schema_v1_minimal.angproj"
    payload = fixture.read_text(encoding="utf-8").replace(
        '"schema_version": 1',
        '"schema_version": 2',
    )
    path = persistence.Path(str(tmp_path)) / "future.angproj"
    path.write_text(payload, encoding="utf-8")
    try:
        persistence.JsonProjectRepository().load(path)
    except persistence.ProjectFormatError:
        return
    raise AssertionError("future project schema must be rejected")
