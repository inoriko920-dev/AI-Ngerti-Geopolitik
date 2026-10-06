"""Local filesystem media-availability adapter."""

from pathlib import Path


class LocalMediaAvailability:
    def status(self, path: Path) -> str:
        return "online" if path.is_file() else "missing"
