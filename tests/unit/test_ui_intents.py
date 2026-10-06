from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntent, UiIntentType


def test_recording_intent_sink_preserves_semantic_intent() -> None:
    sink = RecordingIntentSink()
    intent = UiIntent(UiIntentType.SELECT_ASSET, (("asset_id", "A014"),))
    sink(intent)
    assert sink.intents == [intent]
