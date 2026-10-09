"""Strict fail-closed mapping of frozen UI-042 export options to Pilot A.

The modal appearance is unchanged; unsupported options must never silently
produce video with ignored audio, subtitles, codec or quality selections.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState


class StillExportIntentError(ValueError):
    """Safe, actionable Indonesian export rejection without private paths."""


_RESOLUTIONS: dict[str, tuple[int, int]] = {
    "1920 × 1080 (Full HD)": (1920, 1080),
    "2560 × 1440": (2560, 1440),
    "3840 × 2160 (4K)": (3840, 2160),
}
_FIELDS = frozenset(
    {
        "action",
        "output_directory",
        "output_name",
        "format",
        "preset",
        "resolution",
        "fps",
        "quality",
        "sharpen",
        "subtitle",
    }
)
_FORBIDDEN = frozenset('<>:"/\\|?*')
_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {
    f"LPT{i}" for i in range(1, 10)
}


def validate_still_export_intent(payload: Mapping[str, str], state: ProjectState) -> Path:
    """Permit only unchanged-resolution/FPS silent H.264 on the original scene timeline."""
    if set(payload) != _FIELDS or payload.get("action") != "render_requested":
        raise StillExportIntentError("Permintaan render tidak lengkap. Buka Ekspor Video lagi.")
    if payload["format"] != "MP4 (H.264)":
        raise StillExportIntentError("Pilot A baru mendukung MP4 H.264.")
    if payload["preset"] != "Kualitas Tinggi (Rekomendasi)" or payload["quality"] != "78":
        raise StillExportIntentError("Preset atau bitrate ini belum didukung oleh Pilot A.")
    if payload["sharpen"] != "Normal":
        raise StillExportIntentError("Ketajaman pilihan ini belum didukung oleh Pilot A.")
    if payload["subtitle"] != "Tanpa Subtitle":
        raise StillExportIntentError("Burn-in subtitle belum tersedia; pilih Tanpa Subtitle.")
    if state.subtitle is not None or state.narration is not None:
        raise StillExportIntentError("Project berisi subtitle/narasi; ekspor audio-video belum didukung.")
    if not state.tracks or not any(track.clips for track in state.tracks):
        raise StillExportIntentError("Project belum mempunyai scene gambar untuk diekspor.")
    if any(asset.media_type != "image" or asset.has_audio for asset in state.assets):
        raise StillExportIntentError("Pilot A hanya mendukung gambar, bukan video/audio.")
    if any(clip.image_hold_frames is None for track in state.tracks for clip in track.clips):
        raise StillExportIntentError("Timeline berisi klip yang belum didukung ekspor gambar.")
    selected = _RESOLUTIONS.get(payload["resolution"])
    if selected != (state.settings.width, state.settings.height):
        raise StillExportIntentError(
            "Resolusi harus sama dengan resolusi project; konversi belum didukung."
        )
    if payload["fps"] != f"{state.fps} fps":
        raise StillExportIntentError("FPS harus sama dengan FPS project; konversi belum didukung.")
    name = payload["output_name"].strip()
    if name.lower().endswith(".mp4"):
        name = name[:-4]
    if (
        not 1 <= len(name) <= 180
        or name.startswith(".")
        or name.endswith((" ", "."))
        or name.split(".")[0].upper() in _RESERVED
        or any(char in _FORBIDDEN or ord(char) < 32 for char in name)
    ):
        raise StillExportIntentError("Nama output MP4 tidak valid.")
    folder = Path(payload["output_directory"])
    if (
        not folder.is_absolute()
        or not folder.is_dir()
        or any(path.is_symlink() or path.is_junction() for path in (folder, *folder.parents))
    ):
        raise StillExportIntentError("Pilih folder output lokal yang tersedia dan bukan tautan.")
    output = folder / f"{name}.mp4"
    if output.exists() or output.is_symlink():
        raise StillExportIntentError("MP4 tujuan sudah ada. Pilih nama baru agar tidak tertimpa.")
    return output
