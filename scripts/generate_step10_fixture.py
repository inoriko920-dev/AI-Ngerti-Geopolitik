from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg not found")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=size=1920x1080:rate=30",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=880:sample_rate=48000",
        "-t",
        "8",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "28",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-shortest",
        str(output),
    ]
    subprocess.run(command, check=True, shell=False)
    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit("fixture was not created")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
