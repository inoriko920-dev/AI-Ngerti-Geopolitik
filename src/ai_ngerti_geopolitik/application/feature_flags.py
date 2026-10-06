"""STEP 11 feature/readiness registry.

This registry is intentionally provider/engine agnostic. A flag describes
whether a surface may be exposed as production-ready; it is not a shortcut
around acceptance evidence.
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
        "production_media_engine",
        FeatureState.QUALIFYING,
        "STEP 11 Wave 0 must qualify the Windows production engine.",
    ),
    FeatureFlag(
        "continuous_playback",
        FeatureState.QUALIFYING,
        "Transport semantics exist; native continuous playback needs Wave 0 evidence.",
    ),
    FeatureFlag(
        "libopenshot_direct_binding",
        FeatureState.BLOCKED,
        "Windows build/package/license evidence is not sufficient for production adoption.",
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
