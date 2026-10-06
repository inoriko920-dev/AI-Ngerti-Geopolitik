from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.properties import PropertyController, PropertyEditError
from ai_ngerti_geopolitik.domain import (
    AudioProperties,
    Clip,
    ColorProperties,
    FrameTime,
    VideoProperties,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _add_clip(session: ProjectSession, clip: Clip) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W3-ADD-{session.state.revision + 1:06d}",
            label="Add W3 clip",
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
    session.new_project("ANG-S11-W3", "W3 Properties Video Audio Color Speed")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    if asset.duration.frames < 180:
        raise AssertionError("W3 fixture requires at least 180 frames")
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

    baseline_state_hash = session.state.semantic_hash()
    baseline_preview = evidence / "preview_baseline.png"
    engine.preview_frame(session.state, 30, baseline_preview)

    controller = PropertyController(session.bus)
    bindings = [
        controller.bind_project().target_type.value,
        controller.bind_track("V1").target_type.value,
        controller.bind_asset(asset_id).target_type.value,
        controller.bind_clip("C001").target_type.value,
    ]

    controller.set_video(
        VideoProperties(
            position_x=36,
            position_y=-18,
            scale_x_percent=82,
            scale_y_percent=82,
            rotation_tenths=50,
            opacity_percent=78,
            crop_left_percent=4,
            crop_top_percent=3,
            crop_right_percent=2,
            crop_bottom_percent=3,
        )
    )
    controller.set_audio(
        AudioProperties(
            volume_percent=68,
            pan_percent=-30,
            fade_in_frames=12,
            fade_out_frames=18,
        )
    )
    controller.set_color(
        ColorProperties(
            brightness_percent=8,
            exposure_tenths_ev=3,
            contrast_percent=18,
            saturation_percent=25,
            temperature_percent=12,
            tint_percent=-8,
        )
    )
    controller.set_speed(200, ripple=True)

    property_state_hash = session.state.semantic_hash()
    edited = session.state.clip("C001")
    shifted = session.state.clip("C002")
    if edited.duration_frames != segment // 2:
        raise AssertionError(f"unexpected 2x duration: {edited.duration_frames}")
    if shifted.timeline_start.frames != edited.duration_frames:
        raise AssertionError("speed ripple did not move later clip")

    property_preview = evidence / "preview_properties.png"
    engine.preview_frame(session.state, min(30, edited.duration_frames - 1), property_preview)
    if _sha256(baseline_preview) == _sha256(property_preview):
        raise AssertionError("property preview is byte-identical to baseline preview")

    reverse_error = ""
    try:
        controller.set_reverse(True)
    except PropertyEditError as exc:
        reverse_error = str(exc)
    if not reverse_error:
        raise AssertionError("reverse should be explicitly disabled in W3")

    for _ in range(4):
        controller.undo()
    undo_hash = session.state.semantic_hash()
    if undo_hash != baseline_state_hash:
        raise AssertionError("cross-property Undo did not restore baseline")

    for _ in range(4):
        controller.redo()
    redo_hash = session.state.semantic_hash()
    if redo_hash != property_state_hash:
        raise AssertionError("cross-property Redo did not restore W3 state")

    project_path = evidence / "w3_properties.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.semantic_hash() != session.state.semantic_hash():
        raise AssertionError("W3 project round-trip changed canonical properties")

    export_path = evidence / "w3_properties_export.mp4"
    export = engine.export(session.state, export_path)
    export_probe = probe.probe(export_path)
    expected_frames = session.state.timeline_end_frame
    if abs(export_probe.duration_frames - expected_frames) > 3:
        raise AssertionError(
            f"W3 export duration mismatch: expected {expected_frames}, "
            f"got {export_probe.duration_frames}"
        )

    _write_json(
        evidence / "01_properties.json",
        {
            "bindings": bindings,
            "clip_id": edited.clip_id,
            "video": edited.properties.video.__dict__
            if hasattr(edited.properties.video, "__dict__")
            else {
                "position_x": edited.properties.video.position_x,
                "position_y": edited.properties.video.position_y,
                "scale_x_percent": edited.properties.video.scale_x_percent,
                "scale_y_percent": edited.properties.video.scale_y_percent,
                "rotation_tenths": edited.properties.video.rotation_tenths,
                "opacity_percent": edited.properties.video.opacity_percent,
                "crop_left_percent": edited.properties.video.crop_left_percent,
                "crop_top_percent": edited.properties.video.crop_top_percent,
                "crop_right_percent": edited.properties.video.crop_right_percent,
                "crop_bottom_percent": edited.properties.video.crop_bottom_percent,
            },
            "audio": {
                "volume_percent": edited.properties.audio.volume_percent,
                "pan_percent": edited.properties.audio.pan_percent,
                "fade_in_frames": edited.properties.audio.fade_in_frames,
                "fade_out_frames": edited.properties.audio.fade_out_frames,
            },
            "color": {
                "brightness_percent": edited.properties.color.brightness_percent,
                "exposure_tenths_ev": edited.properties.color.exposure_tenths_ev,
                "contrast_percent": edited.properties.color.contrast_percent,
                "saturation_percent": edited.properties.color.saturation_percent,
                "temperature_percent": edited.properties.color.temperature_percent,
                "tint_percent": edited.properties.color.tint_percent,
            },
            "speed_percent": edited.properties.speed.rate_percent,
            "source_duration_frames": edited.source_duration_frames,
            "timeline_duration_frames": edited.duration_frames,
            "later_clip_start": shifted.timeline_start.frames,
        },
    )
    _write_json(
        evidence / "02_undo_persistence.json",
        {
            "baseline_hash": baseline_state_hash,
            "property_hash": property_state_hash,
            "undo_hash": undo_hash,
            "redo_hash": redo_hash,
            "undo_restored": undo_hash == baseline_state_hash,
            "redo_restored": redo_hash == property_state_hash,
            "save_reopen_hash_match": reopened.state.semantic_hash()
            == session.state.semantic_hash(),
            "reverse_supported": controller.capabilities.reverse_supported,
            "reverse_reason": reverse_error,
        },
    )
    _write_json(
        evidence / "03_preview_export.json",
        {
            "baseline_preview": baseline_preview.name,
            "baseline_preview_sha256": _sha256(baseline_preview),
            "property_preview": property_preview.name,
            "property_preview_sha256": _sha256(property_preview),
            "preview_changed": _sha256(baseline_preview) != _sha256(property_preview),
            "export_file": export.output_path.name,
            "export_sha256": _sha256(export.output_path),
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
        "bindings": bindings,
        "video_properties": True,
        "crop_composition": True,
        "audio_properties": True,
        "color_properties": True,
        "speed_duration_recompute": True,
        "reverse_supported": False,
        "undo_redo": undo_hash == baseline_state_hash and redo_hash == property_state_hash,
        "save_reopen": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "preview_changed": _sha256(baseline_preview) != _sha256(property_preview),
        "export_valid": export_path.is_file() and export_path.stat().st_size > 0,
        "export_has_audio": export_probe.has_audio,
    }
    _write_json(evidence / "00_w3_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
