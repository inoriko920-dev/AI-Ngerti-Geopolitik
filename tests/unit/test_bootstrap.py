from ai_ngerti_geopolitik.bootstrap.main import FOUNDATION_MESSAGE, run


def test_foundation_entrypoint_is_truthful(capsys) -> None:
    assert run() == 0
    assert capsys.readouterr().out.strip() == FOUNDATION_MESSAGE
    assert "not implemented" in FOUNDATION_MESSAGE
