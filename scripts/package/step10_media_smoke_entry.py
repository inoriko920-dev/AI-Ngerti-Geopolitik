from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository

TOKEN = "ANG_S10_PACKAGED_MEDIA_SMOKE_OK"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    fixture = args.fixture.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, repository, engine)

    asset_id = session.import_media(fixture)
    clip_id = session.add_to_timeline(asset_id)
    right_clip_id = session.split_clip(clip_id, 150)
    session.trim_right(right_clip_id, 30)

    project_path = output_dir / "packaged_smoke.angproj"
    session.save(project_path)
    assert repository.load(project_path).semantic_hash() == session.state.semantic_hash()

    before = session.preview_frame(149, output_dir / "preview_149.png")
    after = session.preview_frame(151, output_dir / "preview_151.png")
    assert before.output_path.is_file()
    assert after.output_path.is_file()
    assert sha256(before.output_path) != sha256(after.output_path)

    export_path = output_dir / "packaged_smoke.mp4"
    result = session.export(export_path)
    assert result.width == 1920
    assert result.height == 1080
    assert result.fps == 30
    assert abs(result.duration_frames - 210) <= 1

    print(TOKEN)
    print(f"project={project_path}")
    print(f"export={export_path}")
    print(f"export_sha256={sha256(export_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
