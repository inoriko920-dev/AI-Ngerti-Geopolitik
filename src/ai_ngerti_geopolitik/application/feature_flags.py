"""STEP 11 feature/readiness registry.

This registry describes evidence-backed readiness. A VERIFIED engine/runtime flag
does not imply every user-facing feature using that engine is already complete.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FeatureState(StrEnum):
    VERIFIED = "verified"
    QUALIFYING = "qualifying"
    BLOCKED = "blocked"
    RESERVED = "reserved"


@dataclass(frozen=True, slots=True)
class FeatureFlag:
    key: str
    state: FeatureState
    reason: str


_FLAGS = (
    FeatureFlag(
        "canonical_editing_backbone",
        FeatureState.VERIFIED,
        "STEP 10 Windows E2E proved import/edit/save/preview/export.",
    ),
    FeatureFlag(
        "mlt_windows_runtime",
        FeatureState.VERIFIED,
        (
            "W0 run 37533447729 proved MLT 7.40.0-2 playback, seek, "
            "Python binding and avformat render on Windows."
        ),
    ),
    FeatureFlag(
        "production_media_engine",
        FeatureState.QUALIFYING,
        (
            "MLT is the accepted primary implementation candidate; final bundled "
            "native package/license chain remains a later release gate."
        ),
    ),
    FeatureFlag(
        "continuous_playback",
        FeatureState.QUALIFYING,
        (
            "Native MLT playback/seek is qualified; real Qt transport integration "
            "is scheduled for W2."
        ),
    ),
    FeatureFlag(
        "libopenshot_direct_binding",
        FeatureState.BLOCKED,
        (
            "Windows build/package evidence plus libopenshot-audio licensing remains "
            "insufficient for direct production adoption."
        ),
    ),
    FeatureFlag(
        "gemini_service",
        FeatureState.RESERVED,
        "Real Gemini/provider wiring is reserved for SF-STEP 12.",
    ),
)

FEATURE_FLAGS = {flag.key: flag for flag in _FLAGS}


def feature_flag(key: str) -> FeatureFlag:
    try:
        return FEATURE_FLAGS[key]
    except KeyError as exc:
        raise KeyError(f"unknown feature flag: {key}") from exc
