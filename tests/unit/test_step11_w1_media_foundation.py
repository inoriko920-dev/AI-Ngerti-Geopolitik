from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandError,
    SetAssetAvailabilityCommand,
    UpdateProjectSettingsCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.media_library import MediaBinController, MediaBinQuery
from ai_ngerti_geopolitik.application.media_status import MediaStatusService
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.media_status import LocalMediaAvailability
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class Probe:
    def probe(self, path: Path) -> ProbeResult:
        suffix = path.suffix.lower()
        if suffix == ".mp4":
            return ProbeResult(
                path,
                90,
                30,
                1280,
                720,
                True,
                "a" * 64,
                "video",
                3.0,
                100,
                48000,
            )
        if suffix == ".wav":
            return ProbeResult(
                path,
                0,
                0,
                0,
                0,
                True,
                "b" * 64,
                "audio",
                2.0,
                80,
                48000,
            )
        return ProbeResult(
            path,
            1,
            0,
            800,
            600,
            False,
            "c" * 64,
            "image",
            0.0,
            60,
            0,
        )


def _session() -> ProjectSession:
    session = ProjectSession(JsonProjectRepository())
    session.new_project("P-MEDIA", "Media")
    return session


def test_video_audio_image_import_and_media_bin_query(tmp_path: Path) -> None:
    session = _session()
    importer = MediaImportService(Probe())
    video = importer.import_path(session, tmp_path / "z-video.mp4")
    audio = importer.import_path(session, tmp_path / "a-audio.wav")
    image = importer.import_path(session, tmp_path / "m-image.png")

    assert (video, audio, image) == ("A001", "A002", "A003")
    assert [item.media_type for item in session.state.assets] == ["video", "audio", "image"]
    assert session.state.asset(audio).duration.frames == 60
    assert session.state.asset(image).duration.frames == 1

    media_bin = MediaBinController(lambda: session.state)
    media_bin.select(audio)
    audio_items = media_bin.query(MediaBinQuery(media_types=("audio",), sort_by="name"))
    assert [item.asset_id for item in audio_items] == ["A002"]
    assert audio_items[0].selected
    search = media_bin.query(MediaBinQuery(text="image"))
    assert [item.asset_id for item in search] == ["A003"]


def test_duplicate_media_path_is_atomic_and_ids_remain_stable(tmp_path: Path) -> None:
    session = _session()
    importer = MediaImportService(Probe())
    path = tmp_path / "clip.mp4"
    assert importer.import_path(session, path) == "A001"
    revision = session.state.revision
    with pytest.raises(CommandError):
        importer.import_path(session, path)
    assert session.state.revision == revision
    assert [asset.asset_id for asset in session.state.assets] == ["A001"]


def test_missing_media_keeps_existing_clip_and_asset_identity(tmp_path: Path) -> None:
    session = _session()
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"fixture")
    importer = MediaImportService(Probe())
    asset_id = importer.import_path(session, path)
    asset = session.state.asset(asset_id)
    clip = Clip(
        "C001",
        asset_id,
        FrameTime(0, 30),
        FrameTime(0, 30),
        asset.duration,
    )
    session.execute(
        CommandBatch(
            "ADD",
            "add clip",
            "manual",
            session.state.revision,
            (AddClipCommand(clip),),
        )
    )

    path.unlink()
    changed = MediaStatusService(LocalMediaAvailability()).refresh(session)
    assert changed == ("A001",)
    assert session.state.asset("A001").availability == "missing"
    assert session.state.clip("C001").asset_id == "A001"
    assert len(session.state.track("V1").clips) == 1

    session.execute(
        CommandBatch(
            "OFFLINE",
            "mark offline",
            "manual",
            session.state.revision,
            (SetAssetAvailabilityCommand("A001", "offline"),),
        )
    )
    assert session.state.asset("A001").availability == "offline"
    assert session.state.clip("C001").asset_id == "A001"


def test_fps_change_is_blocked_after_media_import(tmp_path: Path) -> None:
    session = _session()
    MediaImportService(Probe()).import_path(session, tmp_path / "clip.mp4")
    with pytest.raises(CommandError):
        session.execute(
            CommandBatch(
                "FPS",
                "change fps",
                "manual",
                session.state.revision,
                (UpdateProjectSettingsCommand(1920, 1080, 60, "16:9"),),
            )
        )
