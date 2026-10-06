from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    import mlt7 as mlt

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    mlt.Factory().init()
    profile = mlt.Profile()
    producer = mlt.Producer(profile, str(source))
    if not producer.is_valid():
        raise RuntimeError(f"MLT producer could not open {source}")

    length = int(producer.get_length())
    if length < 4:
        raise RuntimeError(f"MLT producer length unexpectedly short: {length}")

    requested = sorted({0, min(10, length - 1), length // 2, max(0, length - 2)})
    frames: list[dict[str, int]] = []
    for position in requested:
        producer.seek(position)
        frame = producer.get_frame()
        if frame is None:
            raise RuntimeError(f"MLT returned no frame at {position}")
        frames.append(
            {
                "requested_position": position,
                "frame_position": int(frame.get_position()),
            }
        )

    payload = {
        "binding": "mlt7",
        "producer_valid": True,
        "length_frames": length,
        "seek_samples": frames,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
