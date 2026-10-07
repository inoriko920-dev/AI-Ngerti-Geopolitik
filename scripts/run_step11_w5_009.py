from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    SetSubtitleAnimationCommand,
    SetSubtitleStyleCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.narration import NarrationImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.application.subtitle_working_copy import (
    SubtitleWorkingCopy,
    SubtitleWorkingCopyService,
)
from ai_ngerti_geopolitik.domain import (
    Clip,
    FrameTime,
    SubtitleAnimation,
    SubtitleStyle,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser, Utf8SrtWriter


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _generate_narration(ffmpeg: str, output: Path) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000",
            "-t",
            "4",
            "-c:a",
            "pcm_s16le",
            str(output),
        ],
        check=True,
        shell=False,
    )


def _extract_frame(ffmpeg: str, source: Path, seconds: float, output: Path) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{seconds:.6f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            str(output),
        ],
        check=True,
        shell=False,
    )
    if not output.is_file() or output.stat().st_size == 0:
        raise AssertionError(f"failed to extract export frame: {output}")


def _mean_band_volume_db(
    ffmpeg: str,
    source: Path,
    *,
    start_seconds: float,
    duration_seconds: float,
) -> float:
    null_output = "NUL" if shutil.which("cmd") else "/dev/null"
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-ss",
            f"{start_seconds:.6f}",
            "-t",
            f"{duration_seconds:.6f}",
            "-i",
            str(source),
            "-af",
            "bandpass=f=440:width_type=h:w=80,volumedetect",
            "-f",
            "null",
            null_output,
        ],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"audio analysis failed: {result.stderr[-1200:]}")
    match = re.findall(r"mean_volume:\s*(-?inf|-?[0-9.]+) dB", result.stderr)
    if not match:
        raise AssertionError("mean_volume was not reported")
    value = match[-1]
    return -120.0 if value == "-inf" else float(value)


def _animation(preset: str) -> SubtitleAnimation:
    timing = 30 if preset == "Clean Documentary" else 18
    return SubtitleAnimation(
        preset=preset,
        enter_frames=timing,
        exit_frames=timing,
        intensity_percent=120,
    )


def _style() -> SubtitleStyle:
    return SubtitleStyle(
        font_family="Segoe UI",
        font_size=80,
        fill_color="#FFD166",
        outline_color="#003049",
        outline_width_tenths=50,
        shadow_tenths=30,
        background_box=True,
        background_opacity_percent=60,
        alignment="top_center",
        margin_v=90,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    source_srt = evidence / "source_original.srt"
    source_srt.write_text(
        "1\n00:00:01,000 --> 00:00:04,000\nORIGINAL W5-009 SUBTITLE\n",
        encoding="utf-8",
        newline="\n",
    )
    source_srt_hash = _sha256(source_srt)

    narration_path = evidence / "narration_440hz.wav"

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    _generate_narration(engine.ffmpeg, narration_path)
    narration_source_hash = _sha256(narration_path)

    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-009", "W5 Combined Qualification")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    segment = min(180, asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-009-VIDEO",
            "Add W5-009 video",
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
    base_video_state = session.state

    baseline_export = evidence / "export_video_baseline.mp4"
    engine.export(base_video_state, baseline_export)

    before_frame = 30
    active_frame = 51
    style_frame = 90
    active_seconds = active_frame / session.state.fps

    baseline_before = evidence / "preview_baseline_before.png"
    baseline_active = evidence / "preview_baseline_active.png"
    engine.preview_frame(base_video_state, before_frame, baseline_before)
    engine.preview_frame(base_video_state, active_frame, baseline_active)

    SubtitleImportService(Utf8SrtParser()).import_path(session, source_srt)
    if session.state.subtitle is None:
        raise AssertionError("subtitle import failed")

    working = SubtitleWorkingCopy(session.state.subtitle)
    working.edit_selected(
        text="EDITED COMBINED W5-009",
        start_frame=45,
        end_frame=135,
    )
    edited_copy = evidence / "source_original.edited.srt"
    SubtitleWorkingCopyService(Utf8SrtWriter()).save_copy_and_commit(
        session,
        working,
        edited_copy,
    )
    if session.state.subtitle is None:
        raise AssertionError("edited subtitle commit failed")

    edited_default_state = session.state
    default_style_preview = evidence / "preview_default_style.png"
    engine.preview_frame(edited_default_state, style_frame, default_style_preview)

    session.execute(
        CommandBatch(
            "W5-009-STYLE",
            "Apply combined subtitle style",
            "manual",
            session.state.revision,
            (SetSubtitleStyleCommand(_style()),),
        )
    )
    styled_state = session.state
    styled_preview = evidence / "preview_styled.png"
    engine.preview_frame(styled_state, style_frame, styled_preview)
    if _sha256(default_style_preview) == _sha256(styled_preview):
        raise AssertionError("qualified subtitle style is not visible in preview")

    NarrationImportService(probe).import_and_bind(
        session,
        narration_path,
        timeline_start_frame=60,
        gain_percent=80,
        fade_in_frames=15,
        fade_out_frames=15,
    )
    combined_static_state = session.state
    if combined_static_state.subtitle is None or combined_static_state.narration is None:
        raise AssertionError("combined subtitle/narration state is incomplete")

    preview_before = evidence / "preview_edited_before_cue.png"
    preview_active = evidence / "preview_edited_inside_cue.png"
    engine.preview_frame(combined_static_state, before_frame, preview_before)
    engine.preview_frame(combined_static_state, active_frame, preview_active)

    if _sha256(preview_before) != _sha256(baseline_before):
        raise AssertionError("subtitle appeared before edited canonical IN frame")
    if _sha256(preview_active) == _sha256(baseline_active):
        raise AssertionError("edited subtitle did not appear inside canonical cue range")

    narration_preview = evidence / "preview_narration.wav"
    engine.preview_narration_audio(
        combined_static_state,
        timeline_frame=75,
        duration_frames=30,
        output_path=narration_preview,
    )
    narration_preview_440 = _mean_band_volume_db(
        engine.ffmpeg,
        narration_preview,
        start_seconds=0.0,
        duration_seconds=0.9,
    )
    if narration_preview_440 < -35.0:
        raise AssertionError("narration preview is not audibly qualified")

    static_export = evidence / "export_static_subtitle_narration.mp4"
    engine.export(combined_static_state, static_export)
    static_export_frame = evidence / "export_static_frame.png"
    _extract_frame(engine.ffmpeg, static_export, active_seconds, static_export_frame)

    baseline_export_frame = evidence / "export_baseline_frame.png"
    _extract_frame(engine.ffmpeg, baseline_export, active_seconds, baseline_export_frame)
    if _sha256(static_export_frame) == _sha256(baseline_export_frame):
        raise AssertionError("combined export does not visibly contain subtitle")

    baseline_mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        baseline_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )

    presets = ("Fade", "Pop", "Slide Up", "Clean Documentary")
    preview_hashes: dict[str, str] = {}
    export_frame_hashes: dict[str, str] = {}
    export_audio_440: dict[str, float] = {}
    export_probes: dict[str, dict[str, object]] = {}

    static_preview = evidence / "preview_static_for_animation.png"
    engine.preview_frame(combined_static_state, active_frame, static_preview)
    static_preview_hash = _sha256(static_preview)
    static_export_frame_hash = _sha256(static_export_frame)

    final_export: Path | None = None
    for preset in presets:
        animated_state = SetSubtitleAnimationCommand(_animation(preset)).apply(
            combined_static_state
        )
        safe_name = preset.lower().replace(" ", "_")

        preview = evidence / f"preview_{safe_name}.png"
        engine.preview_frame(animated_state, active_frame, preview)
        preview_hash = _sha256(preview)
        if preview_hash == static_preview_hash:
            raise AssertionError(f"{preset} preview is identical to static subtitle")
        preview_hashes[preset] = preview_hash

        export = evidence / f"export_{safe_name}.mp4"
        engine.export(animated_state, export)
        export_probe = probe.probe(export)
        if not export_probe.has_audio:
            raise AssertionError(f"{preset} combined export lost audio")
        if abs(export_probe.duration_frames - animated_state.timeline_end_frame) > 3:
            raise AssertionError(f"{preset} combined export duration outside tolerance")
        export_frame = evidence / f"export_{safe_name}_frame.png"
        _extract_frame(engine.ffmpeg, export, active_seconds, export_frame)
        export_frame_hash = _sha256(export_frame)
        if export_frame_hash == static_export_frame_hash:
            raise AssertionError(f"{preset} export frame is identical to static subtitle")
        export_frame_hashes[preset] = export_frame_hash

        audio_440 = _mean_band_volume_db(
            engine.ffmpeg,
            export,
            start_seconds=3.0,
            duration_seconds=0.5,
        )
        if audio_440 < baseline_mid_440 + 8.0:
            raise AssertionError(f"{preset} export does not retain narration audio")
        export_audio_440[preset] = audio_440
        export_probes[preset] = {
            "duration_frames": export_probe.duration_frames,
            "width": export_probe.width,
            "height": export_probe.height,
            "fps": export_probe.fps,
            "has_audio": export_probe.has_audio,
            "sha256": _sha256(export),
        }
        if preset == "Slide Up":
            final_export = export

    if final_export is None:
        raise AssertionError("final combined Slide Up export missing")

    session.execute(
        CommandBatch(
            "W5-009-FINAL-ANIMATION",
            "Apply final combined animation",
            "manual",
            session.state.revision,
            (SetSubtitleAnimationCommand(_animation("Slide Up")),),
        )
    )
    project_path = evidence / "w5_009_combined.angproj"
    session.save(project_path)

    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.semantic_hash() != session.state.semantic_hash():
        raise AssertionError("combined project save/reopen changed canonical state")
    if reopened.state.subtitle is None or reopened.state.narration is None:
        raise AssertionError("subtitle/narration missing after reopen")
    cue = reopened.state.subtitle.cues[0]
    if cue.text != "EDITED COMBINED W5-009":
        raise AssertionError("edited subtitle text did not survive reopen")
    if cue.start.frames != 45 or cue.end.frames != 135:
        raise AssertionError("edited subtitle timing did not survive reopen")
    if reopened.state.subtitle.style != _style():
        raise AssertionError("subtitle style did not survive reopen")
    if reopened.state.subtitle.animation != _animation("Slide Up"):
        raise AssertionError("subtitle animation did not survive reopen")
    if reopened.state.narration.timeline_start.frames != 60:
        raise AssertionError("narration offset did not survive reopen")

    reopened_preview = evidence / "preview_reopened.png"
    engine.preview_frame(reopened.state, active_frame, reopened_preview)
    if _sha256(reopened_preview) != preview_hashes["Slide Up"]:
        raise AssertionError("reopened preview differs from accepted Slide Up state")

    edited_parsed = Utf8SrtParser().parse(edited_copy)
    if edited_parsed[0].text != "EDITED COMBINED W5-009":
        raise AssertionError("saved edited SRT copy lost edited text")
    if edited_parsed[0].start_milliseconds != 1500:
        raise AssertionError("saved edited SRT copy lost edited IN timing")
    if edited_parsed[0].end_milliseconds != 4500:
        raise AssertionError("saved edited SRT copy lost edited OUT timing")

    final_probe = probe.probe(final_export)
    pre_offset_440 = _mean_band_volume_db(
        engine.ffmpeg,
        final_export,
        start_seconds=0.75,
        duration_seconds=0.5,
    )
    final_mid_440 = _mean_band_volume_db(
        engine.ffmpeg,
        final_export,
        start_seconds=3.0,
        duration_seconds=0.5,
    )
    if final_mid_440 < pre_offset_440 + 8.0:
        raise AssertionError("final combined export narration offset is not measurable")

    source_unchanged = _sha256(source_srt) == source_srt_hash
    narration_unchanged = _sha256(narration_path) == narration_source_hash
    if not source_unchanged:
        raise AssertionError("source SRT was modified")
    if not narration_unchanged:
        raise AssertionError("source narration audio was modified")

    _write_json(
        evidence / "01_subtitle_edit_style.json",
        {
            "source_srt_sha256": source_srt_hash,
            "source_srt_unchanged": source_unchanged,
            "edited_copy": str(edited_copy),
            "edited_text": cue.text,
            "start_frame": cue.start.frames,
            "end_frame": cue.end.frames,
            "style": {
                "font_family": reopened.state.subtitle.style.font_family,
                "font_size": reopened.state.subtitle.style.font_size,
                "fill_color": reopened.state.subtitle.style.fill_color,
                "outline_color": reopened.state.subtitle.style.outline_color,
                "background_box": reopened.state.subtitle.style.background_box,
                "alignment": reopened.state.subtitle.style.alignment,
                "margin_v": reopened.state.subtitle.style.margin_v,
            },
            "style_preview_changed": _sha256(default_style_preview) != _sha256(styled_preview),
            "before_cue_matches_baseline": _sha256(preview_before) == _sha256(baseline_before),
            "inside_cue_differs_from_baseline": _sha256(preview_active) != _sha256(baseline_active),
        },
    )
    _write_json(
        evidence / "02_animation_matrix.json",
        {
            "presets": list(presets),
            "static_preview_sha256": static_preview_hash,
            "preview_hashes": preview_hashes,
            "static_export_frame_sha256": static_export_frame_hash,
            "export_frame_hashes": export_frame_hashes,
            "export_audio_440_mean_db": export_audio_440,
            "export_probes": export_probes,
            "all_previews_changed": all(
                value != static_preview_hash for value in preview_hashes.values()
            ),
            "all_export_frames_changed": all(
                value != static_export_frame_hash for value in export_frame_hashes.values()
            ),
        },
    )
    _write_json(
        evidence / "03_narration_sync.json",
        {
            "source_sha256": narration_source_hash,
            "source_unchanged": narration_unchanged,
            "timeline_start_frame": reopened.state.narration.timeline_start.frames,
            "preview_440_mean_db": narration_preview_440,
            "baseline_export_440_mean_db": baseline_mid_440,
            "pre_offset_440_mean_db": pre_offset_440,
            "final_mid_440_mean_db": final_mid_440,
            "offset_proven": final_mid_440 >= pre_offset_440 + 8.0,
            "audible_over_baseline": final_mid_440 >= baseline_mid_440 + 8.0,
        },
    )
    _write_json(
        evidence / "04_persistence_output.json",
        {
            "save_reopen_hash_match": reopened.state.semantic_hash()
            == session.state.semantic_hash(),
            "subtitle_and_narration_present": (
                reopened.state.subtitle is not None and reopened.state.narration is not None
            ),
            "final_export": str(final_export),
            "duration_frames": final_probe.duration_frames,
            "expected_frames": reopened.state.timeline_end_frame,
            "duration_within_tolerance": abs(
                final_probe.duration_frames - reopened.state.timeline_end_frame
            )
            <= 3,
            "width": final_probe.width,
            "height": final_probe.height,
            "fps": final_probe.fps,
            "has_audio": final_probe.has_audio,
            "final_export_sha256": _sha256(final_export),
        },
    )

    report = {
        "status": "PASS",
        "source_srt_unchanged": source_unchanged,
        "edited_text_timing_persisted": (
            cue.text == "EDITED COMBINED W5-009"
            and cue.start.frames == 45
            and cue.end.frames == 135
        ),
        "subtitle_timing_preview_proven": (
            _sha256(preview_before) == _sha256(baseline_before)
            and _sha256(preview_active) != _sha256(baseline_active)
        ),
        "style_visible": _sha256(default_style_preview) != _sha256(styled_preview),
        "all_enabled_animations_preview_rendered": all(
            value != static_preview_hash for value in preview_hashes.values()
        ),
        "all_enabled_animations_export_rendered": all(
            value != static_export_frame_hash for value in export_frame_hashes.values()
        ),
        "narration_preview_audible": narration_preview_440 >= -35.0,
        "narration_frame_sync_proven": final_mid_440 >= pre_offset_440 + 8.0,
        "subtitle_narration_coexist_same_export": (
            bool(export_frame_hashes["Slide Up"]) and final_mid_440 >= baseline_mid_440 + 8.0
        ),
        "output_valid": (
            final_probe.width == 1920
            and final_probe.height == 1080
            and final_probe.fps == 30
            and final_probe.has_audio
        ),
        "duration_within_tolerance": abs(
            final_probe.duration_frames - reopened.state.timeline_end_frame
        )
        <= 3,
        "save_reopen": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "narration_source_unchanged": narration_unchanged,
        "microphone_hardware_qualifier": "PROVISIONAL",
        "asr_used": False,
        "speech_alignment_claimed": False,
    }
    _write_json(evidence / "00_w5_009_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
