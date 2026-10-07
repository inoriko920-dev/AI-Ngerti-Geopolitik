from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.ports import (
    ParsedSubtitleCue,
    SubtitleParseError,
)
from ai_ngerti_geopolitik.application.subtitle_import import (
    SubtitleImportError,
    SubtitleImportService,
    build_subtitle_track,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser


def _state() -> ProjectState:
    asset = Asset(
        "A001",
        "video.mp4",
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(180, 30),
    )
    state = ProjectState(
        project_id="P-W5-002",
        name="SRT import",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
    )
    state.validate()
    return state


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_parser_accepts_utf8_bom_and_preserves_multiline_text(tmp_path: Path) -> None:
    path = tmp_path / "subtitle.srt"
    path.write_bytes(
        (
            "\ufeff1\r\n"
            "00:00:00,000 --> 00:00:01,000\r\n"
            "Baris satu\r\n"
            "Baris dua\r\n"
            "\r\n"
            "2\r\n"
            "00:00:01,000 --> 00:00:02,500\r\n"
            "Cue kedua\r\n"
        ).encode("utf-8")
    )

    cues = Utf8SrtParser().parse(path)

    assert len(cues) == 2
    assert cues[0].index == 1
    assert cues[0].start_milliseconds == 0
    assert cues[0].end_milliseconds == 1000
    assert cues[0].text == "Baris satu\nBaris dua"
    assert cues[1].text == "Cue kedua\n"


def test_import_maps_to_canonical_frames_is_undoable_and_never_writes_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "subtitle.srt"
    path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nPertama\n\n"
        "2\n00:00:01,500 --> 00:00:03,000\nKedua\n",
        encoding="utf-8",
        newline="\n",
    )
    before = _sha256(path)
    bus = CommandBus(_state())

    track = SubtitleImportService(Utf8SrtParser()).import_path(bus, path)

    assert _sha256(path) == before
    assert bus.state.subtitle == track
    assert track.source_ref == str(path.resolve())
    assert track.cues[0].start.frames == 0
    assert track.cues[0].end.frames == 30
    assert track.cues[1].start.frames == 45
    assert track.cues[1].end.frames == 90
    assert bus.state.revision == 1

    bus.undo()
    assert bus.state.subtitle is None
    assert _sha256(path) == before


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            "1\n00:00:00.000 --> 00:00:01,000\nBad separator\n",
            "invalid timestamp",
        ),
        (
            "1\n00:00:02,000 --> 00:00:01,000\nBackwards\n",
            "after start",
        ),
        (
            "1\n00:00:00,000 --> 00:00:01,000\nFirst\n\n"
            "2\n00:00:00,900 --> 00:00:02,000\nOverlap\n",
            "overlaps",
        ),
        (
            "1\n00:00:01,000 --> 00:00:02,000\nFirst\n\n"
            "2\n00:00:00,000 --> 00:00:00,500\nEarlier\n",
            "chronological",
        ),
        (
            "1\n00:00:00,000 --> 00:00:01,000\nFirst\n\n"
            "1\n00:00:01,000 --> 00:00:02,000\nDuplicate\n",
            "duplicated",
        ),
        (
            "1\n00:00:00,000 --> 00:00:01,000\n   \n",
            "text cannot be empty",
        ),
    ],
)
def test_parser_rejects_malformed_or_noncanonical_srt(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    path = tmp_path / "bad.srt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(SubtitleParseError, match=message):
        Utf8SrtParser().parse(path)


def test_parser_rejects_non_utf8_and_wrong_extension(tmp_path: Path) -> None:
    bad_encoding = tmp_path / "bad.srt"
    bad_encoding.write_bytes(b"1\n00:00:00,000 --> 00:00:01,000\n\xff\n")
    with pytest.raises(SubtitleParseError, match="UTF-8"):
        Utf8SrtParser().parse(bad_encoding)

    wrong_extension = tmp_path / "subtitle.txt"
    wrong_extension.write_text("x", encoding="utf-8")
    with pytest.raises(SubtitleParseError, match="\.srt"):
        Utf8SrtParser().parse(wrong_extension)


def test_frame_conversion_rejects_subframe_cue_and_project_overflow(tmp_path: Path) -> None:
    state = _state()
    with pytest.raises(SubtitleImportError, match="representable frame"):
        build_subtitle_track(
            state,
            tmp_path / "tiny.srt",
            (
                ParsedSubtitleCue(
                    index=1,
                    start_milliseconds=1,
                    end_milliseconds=2,
                    text="too short",
                ),
            ),
        )

    with pytest.raises(SubtitleImportError, match="outside the project timeline"):
        build_subtitle_track(
            state,
            tmp_path / "late.srt",
            (
                ParsedSubtitleCue(
                    index=1,
                    start_milliseconds=5000,
                    end_milliseconds=7000,
                    text="too late",
                ),
            ),
        )


def test_frame_conversion_detects_overlap_created_by_project_fps(tmp_path: Path) -> None:
    with pytest.raises(SubtitleImportError, match="overlaps after conversion"):
        build_subtitle_track(
            _state(),
            tmp_path / "precision.srt",
            (
                ParsedSubtitleCue(
                    index=1,
                    start_milliseconds=0,
                    end_milliseconds=50,
                    text="first",
                ),
                ParsedSubtitleCue(
                    index=2,
                    start_milliseconds=49,
                    end_milliseconds=100,
                    text="second",
                ),
            ),
        )
