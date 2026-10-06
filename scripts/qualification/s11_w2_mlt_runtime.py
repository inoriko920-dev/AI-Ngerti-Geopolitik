from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.mlt_projection import build_mlt_timeline_plan
from ai_ngerti_geopolitik.infrastructure.mlt_transport import MltProcessPlaybackTransport


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def media_duration_frames(path: Path, fps: int) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(round(float(result.stdout.strip()) * fps))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    source = args.input.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    fps = 30
    duration = media_duration_frames(source, fps)
    if duration < 100:
        raise RuntimeError(f"MLT W2 fixture unexpectedly short: {duration}")

    asset = Asset(
        "A001",
        str(source),
        "video",
        FrameTime(duration, fps),
        640,
        360,
        True,
        file_hash(source),
        source_name=source.name,
        file_size=source.stat().st_size,
        sample_rate=48000,
    )
    clips = (
        Clip("C001", "A001", FrameTime(0, fps), FrameTime(0, fps), FrameTime(45, fps)),
        Clip(
            "C002",
            "A001",
            FrameTime(45, fps),
            FrameTime(60, fps),
            FrameTime(90, fps),
        ),
    )
    state = ProjectState(
        project_id="ANG-S11-W2-MLT",
        name="W2 MLT projection",
        schema_version=1,
        fps=fps,
        revision=7,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips),),
    )
    state.validate()
    plan = build_mlt_timeline_plan(state)

    environment = {
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
    }
    transport = MltProcessPlaybackTransport(environment=environment)
    transport.load(state)
    transport.seek(15)
    sdl_command = transport.command()

    sdl_env = os.environ.copy()
    sdl_env.update(environment)
    sdl = subprocess.run(
        sdl_command,
        check=False,
        timeout=30,
        env=sdl_env,
        capture_output=True,
        text=True,
    )
    if sdl.returncode != 0:
        detail = sdl.stderr[-2000:] if sdl.stderr else sdl.stdout[-2000:]
        raise RuntimeError(f"MLT SDL2 canonical projection failed: {detail}")

    transport.seek(45)
    transport.play()
    time.sleep(0.15)
    process_started = transport.is_playing
    transport.pause()

    rendered = evidence / "w2-mlt-edited.mp4"
    render_command = [
        "melt",
        *plan.melt_source_arguments(0),
        "-consumer",
        f"avformat:{rendered}",
        "vcodec=libx264",
        "acodec=aac",
        "real_time=-1",
    ]
    render = subprocess.run(
        render_command,
        check=False,
        timeout=60,
        capture_output=True,
        text=True,
    )
    if render.returncode != 0:
        detail = render.stderr[-2000:] if render.stderr else render.stdout[-2000:]
        raise RuntimeError(f"MLT W2 avformat render failed: {detail}")
    if not rendered.is_file() or rendered.stat().st_size == 0:
        raise RuntimeError("MLT W2 render output missing")

    payload = {
        "status": "PASS",
        "project_revision": state.revision,
        "timeline_end_frame": plan.timeline_end_frame,
        "clip_ids": [segment.clip_id for segment in plan.segments],
        "sdl2_returncode": sdl.returncode,
        "process_started_before_pause": process_started,
        "seek_15_arguments": plan.melt_source_arguments(15),
        "seek_45_arguments": plan.melt_source_arguments(45),
        "render_file": rendered.name,
        "render_size": rendered.stat().st_size,
    }
    (evidence / "w2-mlt-runtime.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (evidence / "w2-sdl2.log").write_text(
        (sdl.stdout or "") + "\n--- STDERR ---\n" + (sdl.stderr or ""),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
