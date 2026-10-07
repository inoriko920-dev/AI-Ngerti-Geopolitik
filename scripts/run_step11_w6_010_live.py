from __future__ import annotations

import argparse
import json
import os
import time
from contextlib import suppress
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_approval import (
    AIApprovalState,
    AIPlanApprovalService,
)
from ai_ngerti_geopolitik.application.ai_context import L1ContextBuilder
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    CredentialSlotRef,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.gemini_provider import (
    GeminiAIProvider,
    GeminiProviderConfig,
)
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)
from ai_ngerti_geopolitik.infrastructure.windows_credentials import (
    WindowsCredentialStore,
)


def _write(path: Path, data: dict[str, object]) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-live",
        "live-qualification.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "d" * 64,
        availability="offline",
    )
    clip = Clip(
        "clip-live",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(120, fps),
        properties=replace(
            ClipProperties(),
            effects=EffectProperties("Fade", "Drift", 80, False),
        ),
    )
    state = replace(
        ProjectState.create("project-live-w6-010", "Live Gemini W6-010", fps),
        revision=71,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(clip,)),),
    )
    state.validate()
    return state


def _wait(service: AIPlanJobService, job_id: str) -> object:
    deadline = time.monotonic() + 120.0
    while time.monotonic() < deadline:
        snapshot = service.snapshot(job_id)
        if snapshot.state in {
            AIJobState.SUCCESS,
            AIJobState.FAILED,
            AIJobState.CANCELLED,
        }:
            return snapshot
        time.sleep(0.05)
    raise RuntimeError("live Gemini qualification timed out")


def _scan_for_value(root: Path, raw_value: str) -> bool:
    needle = raw_value.encode("utf-8")
    for path in root.rglob("*"):
        if path.is_file() and needle in path.read_bytes():
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    output = evidence / "02_live_qualification.json"

    raw_value = os.environ.get("ANG_W6_LIVE_VALUE", "").strip()
    if not raw_value:
        report = {
            "status": "PROVISIONAL_NO_CREDENTIAL",
            "credential_available": False,
            "request_attempted": False,
            "official_adapter_used": False,
            "windows_secure_store_used": False,
            "canonical_apply": False,
            "raw_credential_in_evidence": False,
        }
        _write(output, report)
        print("W6-010 live qualification: PROVISIONAL_NO_CREDENTIAL")
        return 0

    namespace_suffix = os.environ.get("GITHUB_RUN_ID", "local").strip() or "local"
    secure_store = WindowsCredentialStore(f"AI-Ngerti-Geopolitik/Gemini/W6-010/{namespace_suffix}")
    metadata = InMemoryCredentialStore()
    slots = CredentialSlotService(secure_store, metadata)
    slot_ref = CredentialSlotRef(1)
    bus = CommandBus(_state())
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision

    try:
        wrapped_value = CredentialSecret(raw_value)
        slots.add_or_update(
            1,
            wrapped_value,
            label="Gemini Live Qualification",
        )
        os.environ.pop("ANG_W6_LIVE_VALUE", None)
        del wrapped_value

        pool = CredentialPoolService(slots, secure_store)
        context = L1ContextBuilder().build(bus.state, ("clip-live",))
        request = AIProviderRequest(
            "REQ-W6-010-LIVE",
            bus.state.revision,
            (
                "For clip-live, set enter_effect exactly to Rise and "
                "intensity_percent exactly to 120. Return only the requested L1 plan."
            ),
            context,
        )
        provider = GeminiAIProvider(
            GeminiProviderConfig(
                model="gemini-2.5-flash",
                timeout_seconds=90.0,
                cancellation_poll_seconds=0.1,
                max_output_tokens=2048,
            )
        )

        with AIPlanJobService(provider, pool) as jobs:
            jobs.submit(
                request,
                bus.state,
                ("clip-live",),
                session_id="w6-010-live",
            )
            terminal = _wait(jobs, request.request_id)
            if terminal.state is not AIJobState.SUCCESS:
                report = {
                    "status": "LIVE_FAILED",
                    "credential_available": True,
                    "request_attempted": True,
                    "official_adapter_used": True,
                    "windows_secure_store_used": True,
                    "job_state": terminal.state.value,
                    "provider_error": (
                        terminal.provider_error.value
                        if terminal.provider_error is not None
                        else None
                    ),
                    "plan_error": (
                        terminal.plan_error.value if terminal.plan_error is not None else None
                    ),
                    "credential_error": (
                        terminal.credential_error.value
                        if terminal.credential_error is not None
                        else None
                    ),
                    "raw_credential_in_evidence": False,
                }
                _write(output, report)
                raise RuntimeError("live Gemini request did not produce a verified plan")

            approvals = AIPlanApprovalService(jobs, bus)
            staged = approvals.stage_from_job(
                request.request_id,
                session_id="w6-010-live",
            )
            approvals.approve(staged.approval_id)
            applied = approvals.apply(staged.approval_id)

        effect = bus.state.clip("clip-live").properties.effects
        applied_hash = bus.state.semantic_hash()
        if applied.state is not AIApprovalState.APPLIED:
            raise RuntimeError("live Gemini plan was not applied")
        if effect.enter_effect != "Rise" or effect.intensity_percent != 120:
            raise RuntimeError("live Gemini plan did not follow the bounded L1 instruction")

        undo_hash = bus.undo().semantic_hash()
        redo_hash = bus.redo().semantic_hash()
        report = {
            "status": "PASS",
            "credential_available": True,
            "request_attempted": True,
            "official_adapter_used": True,
            "windows_secure_store_used": True,
            "job_state": "SUCCESS",
            "canonical_apply": True,
            "selected_effect": effect.enter_effect,
            "selected_intensity_percent": effect.intensity_percent,
            "one_revision_apply": applied.applied_revision == before_revision + 1,
            "undo_exact": undo_hash == before_hash,
            "redo_exact": redo_hash == applied_hash,
            "raw_credential_in_evidence": False,
        }
        _write(output, report)
        if _scan_for_value(evidence, raw_value):
            raise RuntimeError("raw credential leaked into W6-010 evidence")
        print("W6-010 live qualification: PASS")
        return 0
    finally:
        with suppress(Exception):
            secure_store.delete_secret(slot_ref)


if __name__ == "__main__":
    raise SystemExit(main())
