from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.application.subtitle_working_copy import (
    DirtySubtitleWorkingCopyError,
    SubtitleWorkingCopy,
    SubtitleWorkingCopyError,
    SubtitleWorkingCopyService,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectState,
    SubtitleCue,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser, Utf8SrtWriter


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
        project_id="P-W5-003",
        name="Subtitle editing",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
    )
    state.validate()
    return state


def _source(tmp_path: Path) -> Path:
    path = tmp_path / "source.srt"
    path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nPertama\n\n"
        "2\n00:00:01,500 --> 00:00:03,000\nKedua\n\n"
        "3\n00:00:03,500 --> 00:00:05,000\nKetiga\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _imported(tmp_path: Path) -> tuple[CommandBus, Path]:
    path = _source(tmp_path)
    bus = CommandBus(_state())
    SubtitleImportService(Utf8SrtParser()).import_path(bus, path)
    assert bus.state.subtitle is not None
    return bus, path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_edit_selected_text_and_timing_is_local_until_commit(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    original = bus.state.subtitle
    assert original is not None
    working = SubtitleWorkingCopy(original)

    working.select("SRT-000002")
    edited = working.edit_selected(
        text="Kedua diedit\nbaris dua",
        start_frame=48,
        end_frame=88,
    )

    assert working.dirty is True
    assert edited.text == "Kedua diedit\nbaris dua"
    assert edited.start.frames == 48
    assert edited.end.frames == 88
    assert bus.state.subtitle == original


def test_invalid_edit_rejected_without_mutating_working_copy(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)
    before = working.cues

    working.select("SRT-000002")
    with pytest.raises(SubtitleWorkingCopyError, match="overlapping"):
        working.edit_selected(start_frame=20)

    assert working.cues == before
    assert working.dirty is False


def test_insert_and_delete_preserve_explicit_indexes(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)

    working.select("SRT-000001")
    inserted = working.insert_after_selected(
        start_frame=31,
        end_frame=40,
        text="Sisipan",
    )
    assert inserted.index == 4
    assert working.selected_cue_id == inserted.cue_id
    assert [cue.index for cue in working.cues] == [1, 4, 2, 3]

    removed = working.delete_selected()
    assert removed.cue_id == inserted.cue_id
    assert [cue.index for cue in working.cues] == [1, 2, 3]


def test_delete_last_cue_is_rejected() -> None:
    single = SubtitleCue(
        "ONE",
        1,
        FrameTime(0, 30),
        FrameTime(30, 30),
        "Satu",
    )
    from ai_ngerti_geopolitik.domain import SubtitleTrack

    working = SubtitleWorkingCopy(SubtitleTrack("one.srt", (single,)))
    with pytest.raises(SubtitleWorkingCopyError, match="last subtitle cue"):
        working.delete_selected()


def test_split_requires_explicit_text_and_merge_is_deterministic(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)

    working.select("SRT-000002")
    left, right = working.split_selected(
        split_frame=70,
        left_text="Kedua A",
        right_text="Kedua B",
    )
    assert left.end.frames == 70
    assert right.start.frames == 70
    assert right.index == 4
    assert working.selected_cue_id == right.cue_id

    working.select(left.cue_id)
    merged = working.merge_selected_with_next(merged_text="Kedua kembali")
    assert merged.start.frames == 45
    assert merged.end.frames == 90
    assert merged.text == "Kedua kembali"
    assert len(working.cues) == 3


def test_sort_and_index_normalization_are_explicit(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)

    working.select("SRT-000001")
    inserted = working.insert_after_selected(
        start_frame=151,
        end_frame=165,
        text="Posisi list sengaja belum kronologis",
        index=9,
    )
    assert [cue.cue_id for cue in working.cues][1] == inserted.cue_id
    assert [cue.index for cue in working.cues] == [1, 9, 2, 3]

    with pytest.raises(SubtitleWorkingCopyError, match="sorted/validated"):
        working.build_track()

    working.sort_by_time()
    assert working.cues[-1].cue_id == inserted.cue_id
    assert [cue.index for cue in working.cues] == [1, 2, 3, 9]

    working.normalize_indexes()
    assert [cue.index for cue in working.cues] == [1, 2, 3, 4]


def test_dirty_guard_requires_explicit_discard_for_reload(tmp_path: Path) -> None:
    bus, _path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)
    original = bus.state.subtitle

    working.edit_selected(text="Belum disimpan")
    with pytest.raises(DirtySubtitleWorkingCopyError, match="explicit discard"):
        working.reload(original)

    working.reload(original, discard_dirty=True)
    assert working.dirty is False
    assert working.cues == original.cues


def test_save_copy_preserves_source_commits_new_binding_and_is_undoable(
    tmp_path: Path,
) -> None:
    bus, source = _imported(tmp_path)
    assert bus.state.subtitle is not None
    imported = bus.state.subtitle
    before_source = _sha256(source)
    working = SubtitleWorkingCopy(imported)
    working.edit_selected(text="Pertama diedit")
    service = SubtitleWorkingCopyService(Utf8SrtWriter())

    output = service.save_copy_and_commit(bus, working)

    assert output == tmp_path / "source.edited.srt"
    assert output.is_file()
    assert _sha256(source) == before_source
    assert working.dirty is False
    assert bus.state.subtitle is not None
    assert bus.state.subtitle.source_ref == str(output.resolve())
    assert bus.state.subtitle.cues[0].text == "Pertama diedit"
    parsed = Utf8SrtParser().parse(output)
    assert parsed[0].text == "Pertama diedit"

    bus.undo()
    assert bus.state.subtitle == imported
    assert _sha256(source) == before_source


def test_save_copy_refuses_source_path_and_existing_destination(tmp_path: Path) -> None:
    bus, source = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)
    working.edit_selected(text="Edit aman")
    service = SubtitleWorkingCopyService(Utf8SrtWriter())

    with pytest.raises(SubtitleWorkingCopyError, match="cannot be overwritten"):
        service.save_copy_and_commit(bus, working, source)

    existing = tmp_path / "existing.srt"
    existing.write_text("do not clobber", encoding="utf-8")
    original = existing.read_bytes()
    with pytest.raises(SubtitleWorkingCopyError, match="already exists"):
        service.save_copy_and_commit(bus, working, existing)
    assert existing.read_bytes() == original


def test_save_copy_chooses_next_nonexisting_default_name(tmp_path: Path) -> None:
    bus, _source_path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    working = SubtitleWorkingCopy(bus.state.subtitle)
    working.edit_selected(text="Edit")
    (tmp_path / "source.edited.srt").write_text("occupied", encoding="utf-8")
    service = SubtitleWorkingCopyService(Utf8SrtWriter())

    output = service.save_copy_and_commit(bus, working)

    assert output == tmp_path / "source.edited-2.srt"
    assert output.is_file()


def test_writer_preserves_multiline_and_never_clobbers_existing_file(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "copy.srt"
    writer = Utf8SrtWriter()
    from ai_ngerti_geopolitik.application.ports import ParsedSubtitleCue, SubtitleWriteError

    cues = (
        ParsedSubtitleCue(1, 0, 1000, "Baris satu\nBaris dua"),
        ParsedSubtitleCue(2, 1500, 2500, "Cue dua"),
    )
    writer.write_copy(destination, cues)
    parsed = Utf8SrtParser().parse(destination)
    assert parsed[0].text == "Baris satu\nBaris dua"

    with pytest.raises(SubtitleWriteError, match="already exists"):
        writer.write_copy(destination, cues)


def test_failed_writer_does_not_commit_project_binding(tmp_path: Path) -> None:
    bus, _source_path = _imported(tmp_path)
    assert bus.state.subtitle is not None
    imported = bus.state.subtitle
    working = SubtitleWorkingCopy(imported)
    working.edit_selected(text="Edit yang gagal disimpan")

    class FailingWriter:
        def write_copy(self, path: Path, cues: tuple[object, ...]) -> None:
            from ai_ngerti_geopolitik.application.ports import SubtitleWriteError

            raise SubtitleWriteError("simulated writer failure")

    service = SubtitleWorkingCopyService(FailingWriter())  # type: ignore[arg-type]
    with pytest.raises(Exception, match="simulated writer failure"):
        service.save_copy_and_commit(bus, working, tmp_path / "failed.srt")

    assert bus.state.subtitle == imported
    assert working.dirty is True
