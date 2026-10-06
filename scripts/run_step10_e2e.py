from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import threading
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import CommandError
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.application.vertical_slice import (
    VerticalSliceIntentRouter,
    VerticalSliceSession,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
    MediaOperationCancelled,
    MediaToolError,
    MutableCancellationToken,
)
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tool_version(name: str) -> str:
    tool = shutil.which(name)
    if tool is None:
        return "NOT_FOUND"
    import subprocess

    result = subprocess.run(
        [tool, "-version"],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    return (result.stdout or result.stderr).splitlines()[0].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    fixture = args.fixture.resolve()
    evidence = args.evidence.resolve()
    screenshots = evidence / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, repository, engine)
    router = VerticalSliceIntentRouter(session)

    environment = {
        "repo": "inoriko920-dev/AI-Ngerti-Geopolitik",
        "branch": os.environ.get("GITHUB_REF_NAME", "unknown"),
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "ffmpeg_path": shutil.which("ffmpeg"),
        "ffprobe_path": shutil.which("ffprobe"),
        "ffmpeg_version": tool_version("ffmpeg"),
        "ffprobe_version": tool_version("ffprobe"),
        "media_backend_scope": (
            "system FFmpeg qualification adapter; not bundled and not a replacement "
            "decision for D-020 production engine qualification"
        ),
    }
    write_json(evidence / "00_environment.json", environment)

    fixture_hash = sha256(fixture)
    (evidence / "01_input_media_sha256.txt").write_text(
        f"{fixture_hash}  {fixture.name}\n",
        encoding="utf-8",
    )
    (evidence / "01_fixture_provenance.txt").write_text(
        "GENERATED_TEST_FIXTURE\n"
        "Generator: scripts/generate_step10_fixture.py\n"
        "Source: FFmpeg lavfi testsrc2 + sine; no downloaded copyrighted media.\n"
        "Video: 1920x1080 30 fps H.264; Audio: AAC; duration: 8 seconds.\n",
        encoding="utf-8",
    )
    write_json(evidence / "02_ffprobe_input.json", probe.raw_probe(fixture))

    timings: dict[str, float] = {}
    negative_lines: list[str] = []
    initial_hash = session.state.semantic_hash()
    try:
        router(
            UiIntent(
                UiIntentType.IMPORT_MEDIA,
                (("path", str(fixture.with_name("missing.mp4"))),),
            )
        )
        raise AssertionError("missing media unexpectedly imported")
    except MediaToolError as exc:
        negative_lines.append(f"missing-media: PASS: {exc}")
    assert session.state.semantic_hash() == initial_hash

    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QApplication

    from ai_ngerti_geopolitik.presentation.main_window import create_main_window

    app = QApplication.instance() or QApplication(["ANG STEP10 E2E"])
    queued_intents: list[UiIntent] = []
    window = create_main_window(
        "UI-010",
        fixture_mode=True,
        intent_sink=queued_intents.append,
        media_path_provider=lambda: str(fixture),
    )
    import_action = window.window.findChild(QAction, "action_import_media")
    if import_action is None:
        raise AssertionError("real Qt Import Media action not found")
    import_action.trigger()
    app.processEvents()
    if len(queued_intents) != 1:
        raise AssertionError(f"expected one UI intent, got {queued_intents!r}")
    ui_intent = queued_intents.pop()
    if ui_intent.kind is not UiIntentType.IMPORT_MEDIA:
        raise AssertionError(f"unexpected UI intent: {ui_intent.kind}")

    start = time.perf_counter()
    router(ui_intent)
    timings["import_probe_seconds"] = time.perf_counter() - start

    asset_id = router.last_result
    assert asset_id == "A001"
    clip_id = session.add_to_timeline(asset_id)
    assert clip_id == "C001"
    pre_edit_hash = session.state.semantic_hash()
    write_json(
        evidence / "03_pre_edit_snapshot.json",
        session.state.semantic_dict(include_revision=True),
    )

    try:
        session.split_clip(clip_id, 0)
        raise AssertionError("invalid split unexpectedly succeeded")
    except CommandError as exc:
        negative_lines.append(f"invalid-split-atomic: PASS: {exc}")
    assert session.state.semantic_hash() == pre_edit_hash

    right_clip_id = session.split_clip(clip_id, 150)
    post_split_hash = session.state.semantic_hash()
    write_json(
        evidence / "04_post_split_snapshot.json",
        session.state.semantic_dict(include_revision=True),
    )

    session.trim_right(right_clip_id, 30)
    post_trim_hash = session.state.semantic_hash()
    write_json(
        evidence / "05_post_trim_snapshot.json",
        session.state.semantic_dict(include_revision=True),
    )

    hashes = [
        f"pre_edit={pre_edit_hash}",
        f"post_split={post_split_hash}",
        f"post_trim={post_trim_hash}",
    ]
    assert session.undo().semantic_hash() == post_split_hash
    hashes.append(f"undo_trim={session.state.semantic_hash()}")
    assert session.undo().semantic_hash() == pre_edit_hash
    hashes.append(f"undo_split={session.state.semantic_hash()}")
    assert session.redo().semantic_hash() == post_split_hash
    hashes.append(f"redo_split={session.state.semantic_hash()}")
    assert session.redo().semantic_hash() == post_trim_hash
    hashes.append(f"redo_trim={session.state.semantic_hash()}")
    (evidence / "06_undo_redo_hashes.txt").write_text(
        "\n".join(hashes) + "\n",
        encoding="utf-8",
    )

    preview_before = session.preview_frame(149, screenshots / "preview_frame_149.png")
    preview_after = session.preview_frame(151, screenshots / "preview_frame_151.png")
    assert preview_before.project_revision == session.state.revision
    assert preview_after.project_revision == session.state.revision
    assert preview_before.output_path.is_file()
    assert preview_after.output_path.is_file()
    before_hash = sha256(preview_before.output_path)
    after_hash = sha256(preview_after.output_path)
    assert before_hash != after_hash
    (evidence / "07_preview_boundary.txt").write_text(
        "PASS real backend seek on both sides of split boundary\n"
        f"project_revision={session.state.revision}\n"
        f"before_frame=149 sha256={before_hash}\n"
        f"after_frame=151 sha256={after_hash}\n"
        "NOTE continuous interactive playback remains a later production-engine feature; "
        "STEP 10 proves engine-derived seek/output against the edited revision.\n",
        encoding="utf-8",
    )

    projection = session.timeline_projection()
    window.apply_step10_timeline_projection(projection)
    window.apply_step10_preview(preview_after)
    app.processEvents()

    from PySide6.QtWidgets import QLabel

    current = window.stack.currentWidget()
    block_1 = current.findChild(QLabel, "timeline_video_block_1")
    block_2 = current.findChild(QLabel, "timeline_video_block_2")
    preview_canvas = current.findChild(QLabel, "preview_canvas")
    if block_1 is None or block_2 is None or preview_canvas is None:
        raise AssertionError("STEP 10 live UI projection widgets not found")
    assert block_1.text() == "C001  0-150f"
    assert block_2.text() == "C002  150-210f"
    assert window.window.property("step10_project_revision") == projection.project_revision
    assert preview_canvas.property("step10_project_revision") == session.state.revision
    assert preview_canvas.property("step10_timeline_frame") == 151

    live_ui_path = screenshots / "live_ui_projectstate_preview_151.png"
    live_ui = window.render_evidence(1920, 1080)
    if not live_ui.save(str(live_ui_path), "PNG"):
        raise AssertionError(f"failed to save live UI evidence: {live_ui_path}")
    (evidence / "07_live_ui_projection.txt").write_text(
        "PASS ProjectState -> TimelineProjection -> real Qt timeline widgets\n"
        "PASS real backend PreviewResult -> real Qt preview canvas\n"
        f"project_revision={projection.project_revision}\n"
        f"timeline_block_1={block_1.text()}\n"
        f"timeline_block_2={block_2.text()}\n"
        "preview_frame=151\n",
        encoding="utf-8",
    )
    window.close()

    project_path = evidence / "08_saved_project.angproj"
    start = time.perf_counter()
    session.save(project_path)
    timings["save_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    loaded_state = repository.load(project_path)
    timings["load_seconds"] = time.perf_counter() - start
    loaded_hash = loaded_state.semantic_hash()
    assert loaded_hash == post_trim_hash
    assert loaded_state.schema_version == 1
    (evidence / "09_roundtrip_diff.txt").write_text(
        "PASS semantic snapshot identical after .angproj save/load\n"
        f"saved_hash={post_trim_hash}\n"
        f"loaded_hash={loaded_hash}\n",
        encoding="utf-8",
    )

    corrupt = evidence / "broken.angproj"
    corrupt.write_text("{broken", encoding="utf-8")
    try:
        repository.load(corrupt)
        raise AssertionError("corrupt project unexpectedly loaded")
    except ProjectFormatError as exc:
        negative_lines.append(f"corrupt-project: PASS: {exc}")
    corrupt.unlink()

    export_settings = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "codec": "libx264",
        "audio": "aac",
        "expected_duration_frames": 210,
        "backend": "system FFmpeg STEP10 qualification adapter; not bundled",
    }
    write_json(evidence / "10_export_settings.json", export_settings)

    output = evidence / "11_exported_output.mp4"
    start = time.perf_counter()
    result = session.export(output)
    timings["export_seconds"] = time.perf_counter() - start
    assert result.project_revision == session.state.revision
    assert result.width == 1920
    assert result.height == 1080
    assert result.fps == 30
    assert abs(result.duration_frames - 210) <= 1
    write_json(evidence / "12_ffprobe_output.json", probe.raw_probe(output))
    export_hash = sha256(output)
    (evidence / "12_export_sha256.txt").write_text(
        f"{export_hash}  {output.name}\n",
        encoding="utf-8",
    )

    token = MutableCancellationToken()
    cancel_output = evidence / "cancelled_output.mp4"
    cancel_error: list[BaseException] = []

    def export_then_cancel() -> None:
        try:
            session.export(cancel_output, token)
        except BaseException as exc:
            cancel_error.append(exc)

    worker = threading.Thread(target=export_then_cancel, daemon=True)
    worker.start()
    time.sleep(0.03)
    token.cancel()
    worker.join(timeout=15)
    if worker.is_alive():
        raise AssertionError("cancelled export worker did not terminate")
    if not cancel_error or not isinstance(cancel_error[0], MediaOperationCancelled):
        raise AssertionError(f"expected cancellation error, got {cancel_error!r}")
    assert not cancel_output.exists()
    assert not cancel_output.with_name("cancelled_output.partial.mp4").exists()
    negative_lines.append("cancel-export-cleanup: PASS: no final/partial artifact")

    bad_save = evidence / "wrong-extension.json"
    try:
        repository.save(session.state, bad_save)
        raise AssertionError("wrong extension unexpectedly accepted")
    except ProjectFormatError as exc:
        negative_lines.append(f"invalid-project-extension: PASS: {exc}")
    assert not bad_save.exists()

    (evidence / "13_negative_paths.txt").write_text(
        "\n".join(negative_lines) + "\n",
        encoding="utf-8",
    )
    write_json(evidence / "14_timings.json", timings)

    report = {
        "status": "PASS",
        "git_sha": environment["git_sha"],
        "project_revision": session.state.revision,
        "semantic_hash": session.state.semantic_hash(),
        "asset_id": asset_id,
        "clips": ["C001", "C002"],
        "preview_boundary_frames": [149, 151],
        "live_ui_projection": True,
        "timeline_projection_revision": projection.project_revision,
        "project_file": str(project_path),
        "export_file": str(output),
        "export_sha256": export_hash,
        "duration_frames": result.duration_frames,
        "negative_paths": len(negative_lines),
        "ui_entry": "real QAction action_import_media -> semantic UiIntent -> application router",
    }
    write_json(evidence / "15_test_report.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
