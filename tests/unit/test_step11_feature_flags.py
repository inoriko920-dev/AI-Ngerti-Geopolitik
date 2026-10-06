from ai_ngerti_geopolitik.application.feature_flags import (
    FEATURE_FLAGS,
    FeatureState,
    feature_flag,
)


def test_step11_feature_registry_has_unique_truthful_states() -> None:
    assert len(FEATURE_FLAGS) == 6
    assert feature_flag("canonical_editing_backbone").state is FeatureState.VERIFIED
    assert feature_flag("mlt_windows_runtime").state is FeatureState.VERIFIED
    assert feature_flag("production_media_engine").state is FeatureState.QUALIFYING
    assert feature_flag("continuous_playback").state is FeatureState.QUALIFYING
    assert feature_flag("libopenshot_direct_binding").state is FeatureState.BLOCKED
    assert feature_flag("gemini_service").state is FeatureState.RESERVED
