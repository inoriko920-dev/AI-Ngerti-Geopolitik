from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
)
from ai_ngerti_geopolitik.application.creative import (
    CreativeController,
)
from ai_ngerti_geopolitik.application.media_import import (
    MediaImportService,
)
from ai_ngerti_geopolitik.application.project_session import (
    ProjectSession,
)
from ai_ngerti_geopolitik.domain import (
    Clip,
    EffectProperties,
    FrameTime,
    TitleProperties,
    TransitionProperties,
    UNSUPPORTED_LEGACY_EFFECTS,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
)


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def _add_clip(session: ProjectSession, clip: Clip) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W4-ADD-{session.state.revision + 1:06d}",
            label="Add W4 clip",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(AddClipCommand(clip),),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project(
        "ANG-S11-W4",
        "W4 Titles Transitions Effects",
    )

    asset_id = MediaImportService(probe).import_path(
        session,
        video,
    )
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 180:
        raise AssertionError("W4 fixture requires at least 180 frames")
    segment = min(120, asset.duration.frames // 2)

    _add_clip(
        session,
        Clip(
            "C001",
            asset_id,
            FrameTime(0, session.state.fps),
            FrameTime(0, session.state.fps),
            FrameTime(segment, session.state.fps),
        ),
    )
    _add_clip(
        session,
        Clip(
            "C002",
            asset_id,
            FrameTime(segment, session.state.fps),
            FrameTime(segment, session.state.fps),
            FrameTime(segment * 2, session.state.fps),
        ),
    )

    baseline_hash = session.state.semantic_hash()
    baseline_preview = evidence / "preview_baseline.png"
    engine.preview_frame(
        session.state,
        3,
        baseline_preview,
    )

    controller = CreativeController(session.bus)
    controller.bind_clip("C001")
    controller.set_title(
        TitleProperties(
            enabled=True,
            text="AI NGERTI GEOPOLITIK",
            font_size=72,
            position="bottom",
            color_hex="FFFFFF",
            background_opacity_percent=60,
        )
    )
    controller.set_transition(TransitionProperties("fade_black", 12))
    controller.set_effects(
        EffectProperties(
            enter_effect="Rise",
            exit_effect="Fade",
            intensity_percent=120,
            locked=True,
        )
    )

    creative_hash = session.state.semantic_hash()
    edited = session.state.clip("C001")
    creative_preview = evidence / "preview_creative.png"
    engine.preview_frame(
        session.state,
        3,
        creative_preview,
    )
    if _sha256(baseline_preview) == _sha256(creative_preview):
        raise AssertionError("W4 creative preview is byte-identical to baseline")

    for _ in range(3):
        controller.undo()
    undo_hash = session.state.semantic_hash()
    if undo_hash != baseline_hash:
        raise AssertionError("W4 Undo did not restore baseline")

    for _ in range(3):
        controller.redo()
    redo_hash = session.state.semantic_hash()
    if redo_hash != creative_hash:
        raise AssertionError("W4 Redo did not restore creative state")

    project_path = evidence / "w4_creative.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.semantic_hash() != creative_hash:
        raise AssertionError("W4 project round-trip changed canonical state")

    export_path = evidence / "w4_creative_export.mp4"
    export = engine.export(
        session.state,
        export_path,
    )
    export_probe = probe.probe(export_path)
    expected_frames = session.state.timeline_end_frame
    if abs(export_probe.duration_frames - expected_frames) > 3:
        raise AssertionError(
            f"W4 export duration mismatch: expected "
            f"{expected_frames}, got "
            f"{export_probe.duration_frames}"
        )

    _write_json(
        evidence / "01_creative_state.json",
        {
            "clip_id": edited.clip_id,
            "title": {
                "enabled": edited.properties.title.enabled,
                "text": edited.properties.title.text,
                "font_size": edited.properties.title.font_size,
                "position": edited.properties.title.position,
                "color_hex": edited.properties.title.color_hex,
                "background_opacity_percent": (edited.properties.title.background_opacity_percent),
            },
            "transition": {
                "preset": edited.properties.transition.preset,
                "duration_frames": (edited.properties.transition.duration_frames),
            },
            "effects": {
                "enter_effect": (edited.properties.effects.enter_effect),
                "exit_effect": (edited.properties.effects.exit_effect),
                "intensity_percent": (edited.properties.effects.intensity_percent),
                "locked": edited.properties.effects.locked,
            },
            "unsupported_legacy_effects": list(UNSUPPORTED_LEGACY_EFFECTS),
        },
    )
    _write_json(
        evidence / "02_undo_persistence.json",
        {
            "baseline_hash": baseline_hash,
            "creative_hash": creative_hash,
            "undo_hash": undo_hash,
            "redo_hash": redo_hash,
            "undo_restored": undo_hash == baseline_hash,
            "redo_restored": redo_hash == creative_hash,
            "save_reopen_hash_match": (reopened.state.semantic_hash() == creative_hash),
        },
    )
    _write_json(
        evidence / "03_preview_export.json",
        {
            "baseline_preview_sha256": _sha256(baseline_preview),
            "creative_preview_sha256": _sha256(creative_preview),
            "preview_changed": (_sha256(baseline_preview) != _sha256(creative_preview)),
            "export_file": export_path.name,
            "export_sha256": _sha256(export_path),
            "export_frames": export_probe.duration_frames,
            "canonical_timeline_frames": expected_frames,
            "width": export.width,
            "height": export.height,
            "fps": export.fps,
            "has_audio": export_probe.has_audio,
        },
    )
    report = {
        "status": "PASS",
        "title_overlay": edited.properties.title.enabled,
        "transition_fade_black": (edited.properties.transition.preset == "fade_black"),
        "render_backed_effects": (
            edited.properties.effects.enter_effect == "Rise"
            and edited.properties.effects.exit_effect == "Fade"
        ),
        "unsupported_legacy_hidden": (len(UNSUPPORTED_LEGACY_EFFECTS) == 12),
        "crossfade_claimed": False,
        "undo_redo": (undo_hash == baseline_hash and redo_hash == creative_hash),
        "save_reopen": (reopened.state.semantic_hash() == creative_hash),
        "preview_changed": (_sha256(baseline_preview) != _sha256(creative_preview)),
        "export_valid": (export_path.is_file() and export_path.stat().st_size > 0),
        "export_has_audio": export_probe.has_audio,
    }
    _write_json(
        evidence / "00_w4_report.json",
        report,
    )
    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
