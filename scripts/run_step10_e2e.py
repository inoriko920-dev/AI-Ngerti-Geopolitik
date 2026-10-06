from __future__ import annotations

import argparse
import hashlib
import json
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    fixture = args.fixture.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, repository, engine)
    router = VerticalSliceIntentRouter(session)

    environment = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
    }
    write_json(evidence / "00_environment.json", environment)
    (evidence / "01_input_media_sha256.txt").write_text(
        f"{sha256(fixture)}  {fixture.name}\n",
        encoding="utf-8",
    )
    write_json(evidence / "02_ffprobe_input.json", probe.raw_probe(fixture))

    initial_hash = session.state.semantic_hash()
    negative_lines: list[str] = []
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

    router(UiIntent(UiIntentType.IMPORT_MEDIA, (("path", str(fixture)),)))
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

    preview = session.preview_frame(
        151,
        evidence / "screenshots" / "preview_frame_151.png",
    )
    assert preview.project_revision == session.state.revision
    assert preview.output_path.is_file()

    project_path = evidence / "07_saved_project.angproj"
    session.save(project_path)
    loaded_hash = repository.load(project_path).semantic_hash()
    assert loaded_hash == post_trim_hash
    (evidence / "08_roundtrip_diff.txt").write_text(
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
    write_json(evidence / "09_export_settings.json", export_settings)

    output = evidence / "10_exported_output.mp4"
    result = session.export(output)
    assert result.project_revision == session.state.revision
    assert result.width == 1920
    assert result.height == 1080
    assert result.fps == 30
    assert abs(result.duration_frames - 210) <= 1
    write_json(evidence / "11_ffprobe_output.json", probe.raw_probe(output))
    (evidence / "11_export_sha256.txt").write_text(
        f"{sha256(output)}  {output.name}\n",
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

    (evidence / "12_negative_paths.txt").write_text(
        "\n".join(negative_lines) + "\n",
        encoding="utf-8",
    )
    report = {
        "status": "PASS",
        "project_revision": session.state.revision,
        "semantic_hash": session.state.semantic_hash(),
        "asset_id": asset_id,
        "clips": ["C001", "C002"],
        "preview_frame": str(preview.output_path),
        "project_file": str(project_path),
        "export_file": str(output),
        "export_sha256": sha256(output),
        "duration_frames": result.duration_frames,
        "negative_paths": len(negative_lines),
    }
    write_json(evidence / "13_test_report.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
