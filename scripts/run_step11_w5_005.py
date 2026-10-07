from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    SetSubtitleAnimationCommand,
    SetSubtitleCueWordTimingsCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.application.subtitle_word_timing import (
    NOT_SPEECH_ALIGNMENT_LABEL,
    evenly_distribute_words_not_speech_alignment,
)
from ai_ngerti_geopolitik.domain import (
    UNSUPPORTED_SUBTITLE_ANIMATIONS,
    Clip,
    FrameTime,
    SubtitleAnimation,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser


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


def _animation(preset: str) -> SubtitleAnimation:
    timing = 30 if preset == "Clean Documentary" else 18
    return SubtitleAnimation(
        preset=preset,
        enter_frames=timing,
        exit_frames=timing,
        intensity_percent=120,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    source_srt = evidence / "animation_source.srt"
    source_srt.write_text(
        "1\n00:00:01,000 --> 00:00:04,000\nAI ngerti geopolitik\n",
        encoding="utf-8",
        newline="\n",
    )
    source_hash = _sha256(source_srt)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W5-005", "W5 Subtitle Animation")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    segment = min(180, asset.duration.frames)
    session.execute(
        CommandBatch(
            "W5-005-ADD",
            "Add W5-005 video",
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
        raise AssertionError("W5-005 subtitle import failed")

    baseline_state = session.state
    baseline_hash = baseline_state.semantic_hash()
    sample_frame = 36
    sample_seconds = sample_frame / session.state.fps

    baseline_preview = evidence / "preview_none.png"
    engine.preview_frame(baseline_state, sample_frame, baseline_preview)
    baseline_preview_hash = _sha256(baseline_preview)

    baseline_export = evidence / "export_none.mp4"
    engine.export(baseline_state, baseline_export)
    baseline_export_frame = evidence / "export_none_frame.png"
    _extract_frame(engine.ffmpeg, baseline_export, sample_seconds, baseline_export_frame)
    baseline_export_frame_hash = _sha256(baseline_export_frame)

    presets = ("Fade", "Pop", "Slide Up", "Clean Documentary")
    preview_hashes: dict[str, str] = {}
    export_frame_hashes: dict[str, str] = {}
    export_probes: dict[str, dict[str, object]] = {}

    for preset in presets:
        animation = _animation(preset)
        animated_state = SetSubtitleAnimationCommand(animation).apply(baseline_state)

        safe_name = preset.lower().replace(" ", "_")
        preview_path = evidence / f"preview_{safe_name}.png"
        engine.preview_frame(animated_state, sample_frame, preview_path)
        preview_hash = _sha256(preview_path)
        if preview_hash == baseline_preview_hash:
            raise AssertionError(f"{preset} preview is identical to static subtitle")
        preview_hashes[preset] = preview_hash

        export_path = evidence / f"export_{safe_name}.mp4"
        engine.export(animated_state, export_path)
        export_probe = probe.probe(export_path)
        if abs(export_probe.duration_frames - animated_state.timeline_end_frame) > 3:
            raise AssertionError(f"{preset} export duration outside tolerance")
        if not export_probe.has_audio:
            raise AssertionError(f"{preset} export lost audio")

        export_frame = evidence / f"export_{safe_name}_frame.png"
        _extract_frame(engine.ffmpeg, export_path, sample_seconds, export_frame)
        export_frame_hash = _sha256(export_frame)
        if export_frame_hash == baseline_export_frame_hash:
            raise AssertionError(f"{preset} export frame is identical to static subtitle")
        export_frame_hashes[preset] = export_frame_hash
        export_probes[preset] = {
            "frames": export_probe.duration_frames,
            "has_audio": export_probe.has_audio,
            "sha256": _sha256(export_path),
        }

    final_animation = _animation("Slide Up")
    session.execute(
        CommandBatch(
            "W5-005-ANIMATION",
            "Apply qualified subtitle animation",
            "manual",
            session.state.revision,
            (SetSubtitleAnimationCommand(final_animation),),
        )
    )
    animation_hash = session.state.semantic_hash()

    assert session.state.subtitle is not None
    cue = session.state.subtitle.cues[0]
    word_timings = evenly_distribute_words_not_speech_alignment(
        cue,
        acknowledge_not_speech_alignment=True,
    )
    session.execute(
        CommandBatch(
            "W5-005-WORDS",
            "Apply deterministic word timing, NOT speech alignment",
            "manual",
            session.state.revision,
            (SetSubtitleCueWordTimingsCommand(cue.cue_id, word_timings),),
        )
    )
    word_hash = session.state.semantic_hash()

    session.undo()
    if session.state.semantic_hash() != animation_hash:
        raise AssertionError("word-timing Undo did not restore animation-only state")
    session.undo()
    if session.state.semantic_hash() != baseline_hash:
        raise AssertionError("animation Undo did not restore baseline state")
    session.redo()
    session.redo()
    if session.state.semantic_hash() != word_hash:
        raise AssertionError("W5-005 Redo did not restore animation + word timing")

    project_path = evidence / "w5_005_animation.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    if reopened.state.semantic_hash() != session.state.semantic_hash():
        raise AssertionError("W5-005 persistence round-trip changed canonical state")
    if reopened.state.subtitle is None:
        raise AssertionError("W5-005 subtitle missing after reopen")
    if reopened.state.subtitle.animation != final_animation:
        raise AssertionError("W5-005 animation missing after reopen")
    if reopened.state.subtitle.cues[0].word_timings != word_timings:
        raise AssertionError("W5-005 word timing missing after reopen")
    if _sha256(source_srt) != source_hash:
        raise AssertionError("W5-005 changed source SRT")

    _write_json(
        evidence / "01_animation_matrix.json",
        {
            "presets": list(presets),
            "preview_hashes": preview_hashes,
            "baseline_preview_sha256": baseline_preview_hash,
            "all_previews_changed": all(
                value != baseline_preview_hash for value in preview_hashes.values()
            ),
            "export_frame_hashes": export_frame_hashes,
            "baseline_export_frame_sha256": baseline_export_frame_hash,
            "all_export_frames_changed": all(
                value != baseline_export_frame_hash for value in export_frame_hashes.values()
            ),
            "export_probes": export_probes,
        },
    )
    _write_json(
        evidence / "02_word_timing_boundary.json",
        {
            "label": NOT_SPEECH_ALIGNMENT_LABEL,
            "method": "deterministic_even_distribution",
            "asr_used": False,
            "transcription_used": False,
            "speech_alignment_claimed": False,
            "words": [
                {
                    "word_id": item.word_id,
                    "word": item.word,
                    "start_frame": item.start.frames,
                    "end_frame": item.end.frames,
                }
                for item in word_timings
            ],
        },
    )
    _write_json(
        evidence / "03_history_persistence.json",
        {
            "baseline_hash": baseline_hash,
            "animation_hash": animation_hash,
            "word_hash": word_hash,
            "redo_restored": session.state.semantic_hash() == word_hash,
            "save_reopen_hash_match": (
                reopened.state.semantic_hash() == session.state.semantic_hash()
            ),
            "source_srt_unchanged": _sha256(source_srt) == source_hash,
        },
    )
    report = {
        "status": "PASS",
        "fade_render_backed": True,
        "pop_render_backed": True,
        "slide_up_render_backed": True,
        "clean_documentary_render_backed": True,
        "all_previews_changed": all(
            value != baseline_preview_hash for value in preview_hashes.values()
        ),
        "all_export_frames_changed": all(
            value != baseline_export_frame_hash for value in export_frame_hashes.values()
        ),
        "unsupported_presets_hidden": len(UNSUPPORTED_SUBTITLE_ANIMATIONS) == 6,
        "word_timing_persisted": (reopened.state.subtitle.cues[0].word_timings == word_timings),
        "speech_alignment_claimed": False,
        "asr_used": False,
        "undo_redo": session.state.semantic_hash() == word_hash,
        "save_reopen": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "source_srt_unchanged": _sha256(source_srt) == source_hash,
    }
    _write_json(evidence / "00_w5_005_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
