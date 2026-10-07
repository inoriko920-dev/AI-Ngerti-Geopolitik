from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    SetSubtitleStyleCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.domain import Clip, FrameTime, SubtitleStyle
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _render_variant(
    engine: FfmpegSliceMediaEngine,
    baseline_state,
    style: SubtitleStyle,
    frame: int,
    output: Path,
) -> str:
    styled = SetSubtitleStyleCommand(style).apply(baseline_state)
    engine.preview_frame(styled, frame, output)
    return _sha256(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    source_srt = evidence / "style_source.srt"
    source_srt.write_text(
        "1\n00:00:01,000 --> 00:00:04,000\nAI Ngerti Geopolitik\n",
        encoding="utf-8",
        newline="\n",
    )
    source_sha = _sha256(source_srt)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-004", "W5 Subtitle Style")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    segment = min(180, asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-004-ADD",
            "Add W5-004 video",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        asset_id,
                        FrameTime(0, session.state.fps),
                        FrameTime(0, session.state.fps),
                        FrameTime(segment, session.state.fps),
                    )
                ),
            ),
        )
    )
    SubtitleImportService(Utf8SrtParser()).import_path(session, source_srt)
    if session.state.subtitle is None:
        raise AssertionError("W5-004 subtitle import failed")

    baseline_state = session.state
    baseline_hash = baseline_state.semantic_hash()
    frame = 60
    baseline_preview = evidence / "preview_style_baseline.png"
    engine.preview_frame(baseline_state, frame, baseline_preview)
    baseline_preview_hash = _sha256(baseline_preview)

    default = baseline_state.subtitle.style
    variants = {
        "font_family": replace(default, font_family="Segoe UI"),
        "font_size": replace(default, font_size=84),
        "fill_color": replace(default, fill_color="#FFD166"),
        "outline": replace(
            default,
            outline_color="#003049",
            outline_width_tenths=60,
        ),
        "shadow": replace(default, shadow_tenths=50),
        "background": replace(
            default,
            background_box=True,
            background_opacity_percent=70,
        ),
        "alignment": replace(default, alignment="top_center"),
        "margin_v": replace(default, margin_v=180),
    }
    variant_hashes: dict[str, str] = {}
    for name, style in variants.items():
        path = evidence / f"preview_{name}.png"
        digest = _render_variant(
            engine,
            baseline_state,
            style,
            frame,
            path,
        )
        if digest == baseline_preview_hash:
            raise AssertionError(f"style variant did not change preview: {name}")
        variant_hashes[name] = digest

    final_style = SubtitleStyle(
        font_family="Segoe UI",
        font_size=78,
        fill_color="#FFD166",
        outline_color="#003049",
        outline_width_tenths=50,
        shadow_tenths=30,
        background_box=True,
        background_opacity_percent=65,
        alignment="top_center",
        margin_v=90,
    )
    session.execute(
        CommandBatch(
            "W5-004-STYLE",
            "Apply qualified subtitle style",
            "manual",
            session.state.revision,
            (SetSubtitleStyleCommand(final_style),),
        )
    )
    styled_hash = session.state.semantic_hash()
    final_preview = evidence / "preview_style_final.png"
    engine.preview_frame(session.state, frame, final_preview)
    if _sha256(final_preview) == baseline_preview_hash:
        raise AssertionError("final W5-004 style preview is unchanged")

    session.undo()
    undo_hash = session.state.semantic_hash()
    if undo_hash != baseline_hash:
        raise AssertionError("W5-004 Undo did not restore baseline subtitle style")
    session.redo()
    redo_hash = session.state.semantic_hash()
    if redo_hash != styled_hash:
        raise AssertionError("W5-004 Redo did not restore styled subtitle state")

    project_path = evidence / "w5_004_style.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.subtitle is None or reopened.state.subtitle.style != final_style:
        raise AssertionError("W5-004 style did not survive project reopen")
    if reopened.state.semantic_hash() != session.state.semantic_hash():
        raise AssertionError("W5-004 reopen changed canonical state")

    export_path = evidence / "w5_004_style_export.mp4"
    export = engine.export(session.state, export_path)
    export_probe = probe.probe(export_path)
    if abs(export_probe.duration_frames - session.state.timeline_end_frame) > 3:
        raise AssertionError("W5-004 export duration outside tolerance")
    if not export_probe.has_audio:
        raise AssertionError("W5-004 export lost audio")
    if _sha256(source_srt) != source_sha:
        raise AssertionError("W5-004 changed the source SRT")

    style_data = {
        "font_family": final_style.font_family,
        "font_size": final_style.font_size,
        "fill_color": final_style.fill_color,
        "outline_color": final_style.outline_color,
        "outline_width_tenths": final_style.outline_width_tenths,
        "shadow_tenths": final_style.shadow_tenths,
        "background_box": final_style.background_box,
        "background_opacity_percent": final_style.background_opacity_percent,
        "alignment": final_style.alignment,
        "margin_v": final_style.margin_v,
    }
    _write_json(evidence / "01_style_state.json", style_data)
    _write_json(
        evidence / "02_style_preview_matrix.json",
        {
            "baseline_sha256": baseline_preview_hash,
            "variant_sha256": variant_hashes,
            "all_variants_changed": all(
                digest != baseline_preview_hash for digest in variant_hashes.values()
            ),
        },
    )
    _write_json(
        evidence / "03_history_persistence.json",
        {
            "baseline_hash": baseline_hash,
            "styled_hash": styled_hash,
            "undo_hash": undo_hash,
            "redo_hash": redo_hash,
            "undo_restored": undo_hash == baseline_hash,
            "redo_restored": redo_hash == styled_hash,
            "save_reopen_hash_match": (
                reopened.state.semantic_hash() == session.state.semantic_hash()
            ),
        },
    )
    _write_json(
        evidence / "04_export.json",
        {
            "export_sha256": _sha256(export_path),
            "export_frames": export_probe.duration_frames,
            "canonical_timeline_frames": session.state.timeline_end_frame,
            "width": export.width,
            "height": export.height,
            "fps": export.fps,
            "has_audio": export_probe.has_audio,
            "source_srt_sha256": source_sha,
            "source_srt_unchanged": _sha256(source_srt) == source_sha,
        },
    )
    report = {
        "status": "PASS",
        "font_family": True,
        "font_size": True,
        "fill_color": True,
        "outline": True,
        "shadow": True,
        "background_box_opacity": True,
        "alignment": True,
        "safe_vertical_margin": True,
        "undo_redo": undo_hash == baseline_hash and redo_hash == styled_hash,
        "save_reopen": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "preview_matrix_changed": all(
            digest != baseline_preview_hash for digest in variant_hashes.values()
        ),
        "export_valid": export_path.is_file() and export_path.stat().st_size > 0,
        "export_has_audio": export_probe.has_audio,
        "source_srt_unchanged": _sha256(source_srt) == source_sha,
        "subtitle_animation_enabled": False,
    }
    _write_json(evidence / "00_w5_004_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
