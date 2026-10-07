"""Strict SRT parser and no-clobber copy writer for W5 subtitle workflow."""

from __future__ import annotations

import os
import re
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import (
    ParsedSubtitleCue,
    SubtitleParseError,
    SubtitleWriteError,
)

_TIMESTAMP = re.compile(
    r"^(?P<hours>\d{2,}):(?P<minutes>\d{2}):(?P<seconds>\d{2}),(?P<millis>\d{3})$"
)


def _timestamp_milliseconds(value: str, *, cue_index: int) -> int:
    match = _TIMESTAMP.fullmatch(value.strip())
    if match is None:
        raise SubtitleParseError(
            f"SRT cue index {cue_index} has invalid timestamp: {value.strip()!r}"
        )
    hours = int(match.group("hours"))
    minutes = int(match.group("minutes"))
    seconds = int(match.group("seconds"))
    millis = int(match.group("millis"))
    if minutes > 59 or seconds > 59:
        raise SubtitleParseError(
            f"SRT cue index {cue_index} timestamp minute/second is outside 00..59"
        )
    return (((hours * 60) + minutes) * 60 + seconds) * 1000 + millis


def _format_timestamp(milliseconds: int) -> str:
    if milliseconds < 0:
        raise SubtitleWriteError("subtitle timestamp cannot be negative")
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


class Utf8SrtParser:
    """Parse SRT without modifying the source file."""

    def parse(self, path: Path) -> tuple[ParsedSubtitleCue, ...]:
        source = path.expanduser()
        if source.suffix.lower() != ".srt":
            raise SubtitleParseError("subtitle source must use .srt extension")
        if not source.is_file():
            raise SubtitleParseError(f"subtitle source does not exist: {source}")

        try:
            payload = source.read_bytes()
        except OSError as exc:
            raise SubtitleParseError(f"cannot read subtitle source: {source}") from exc

        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise SubtitleParseError("SRT must be valid UTF-8 or UTF-8 with BOM") from exc

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        blocks = [block for block in re.split(r"\n[ \t]*\n", normalized) if block.strip()]
        if not blocks:
            raise SubtitleParseError("SRT does not contain any subtitle cues")

        cues: list[ParsedSubtitleCue] = []
        seen_indexes: set[int] = set()
        previous_start = -1
        previous_end = 0

        for block_number, block in enumerate(blocks, start=1):
            lines = block.rstrip("\n").split("\n")
            if len(lines) < 2:
                raise SubtitleParseError(f"SRT block {block_number} must contain index and timing")
            if len(lines) == 2:
                index_label = lines[0].strip() or str(block_number)
                raise SubtitleParseError(f"SRT cue index {index_label} text cannot be empty")
            try:
                index = int(lines[0].strip())
            except ValueError as exc:
                raise SubtitleParseError(
                    f"SRT block {block_number} has a non-numeric cue index"
                ) from exc
            if index <= 0:
                raise SubtitleParseError(f"SRT block {block_number} cue index must be positive")
            if index in seen_indexes:
                raise SubtitleParseError(f"SRT cue index is duplicated: {index}")
            seen_indexes.add(index)

            timing = lines[1].strip()
            if timing.count("-->") != 1:
                raise SubtitleParseError(
                    f"SRT cue index {index} must contain one '-->' timing separator"
                )
            start_text, end_text = (part.strip() for part in timing.split("-->", 1))
            start_ms = _timestamp_milliseconds(start_text, cue_index=index)
            end_ms = _timestamp_milliseconds(end_text, cue_index=index)
            if end_ms <= start_ms:
                raise SubtitleParseError(f"SRT cue index {index} end timestamp must be after start")

            subtitle_text = "\n".join(lines[2:])
            if not subtitle_text.strip():
                raise SubtitleParseError(f"SRT cue index {index} text cannot be empty")
            if start_ms < previous_start:
                raise SubtitleParseError(f"SRT cue index {index} is out of chronological order")
            if start_ms < previous_end:
                raise SubtitleParseError(f"SRT cue index {index} overlaps the previous cue")

            cues.append(
                ParsedSubtitleCue(
                    index=index,
                    start_milliseconds=start_ms,
                    end_milliseconds=end_ms,
                    text=subtitle_text,
                )
            )
            previous_start = start_ms
            previous_end = end_ms

        return tuple(cues)


class Utf8SrtWriter:
    """Write a new UTF-8 SRT copy without clobbering an existing file."""

    def write_copy(
        self,
        path: Path,
        cues: tuple[ParsedSubtitleCue, ...],
    ) -> None:
        destination = path.expanduser()
        if destination.suffix.lower() != ".srt":
            raise SubtitleWriteError("subtitle copy destination must use .srt extension")
        if not cues:
            raise SubtitleWriteError("subtitle copy requires at least one cue")

        previous_start = -1
        previous_end = 0
        blocks: list[str] = []
        for cue in cues:
            if cue.index <= 0:
                raise SubtitleWriteError("subtitle cue index must be positive")
            if cue.end_milliseconds <= cue.start_milliseconds:
                raise SubtitleWriteError(f"subtitle cue index {cue.index} end must be after start")
            if not cue.text.strip():
                raise SubtitleWriteError(f"subtitle cue index {cue.index} text cannot be empty")
            if cue.start_milliseconds < previous_start:
                raise SubtitleWriteError("subtitle copy cues must be sorted before save")
            if cue.start_milliseconds < previous_end:
                raise SubtitleWriteError("subtitle copy cues cannot overlap")
            blocks.append(
                f"{cue.index}\n"
                f"{_format_timestamp(cue.start_milliseconds)} --> "
                f"{_format_timestamp(cue.end_milliseconds)}\n"
                f"{cue.text}"
            )
            previous_start = cue.start_milliseconds
            previous_end = cue.end_milliseconds

        payload = "\n\n".join(blocks) + "\n"
        destination.parent.mkdir(parents=True, exist_ok=True)
        created = False
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as handle:
                created = True
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise SubtitleWriteError(
                f"subtitle copy destination already exists: {destination}"
            ) from exc
        except OSError as exc:
            if created and destination.exists():
                try:
                    destination.unlink()
                except OSError:
                    pass
            raise SubtitleWriteError(f"cannot write subtitle copy: {destination}") from exc
