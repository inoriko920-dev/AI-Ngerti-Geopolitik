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
_RESERVED = (
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


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
    want_subtitles = payload["subtitle"] == "Sertakan Subtitle (Burn-in ke Video)"
    if payload["subtitle"] not in {"Tanpa Subtitle", "Sertakan Subtitle (Burn-in ke Video)"}:
        raise StillExportIntentError("Pilihan subtitle tidak dikenali.")
    if want_subtitles != bool(state.subtitle is not None and state.subtitle.enabled):
        raise StillExportIntentError("Subtitle project wajib sesuai dengan pilihan ekspor.")
    if (
        want_subtitles
        and state.subtitle is not None
        and (
            state.subtitle.animation.preset != "none"
            or state.subtitle.style.font_family != "Arial"
        )
    ):
        raise StillExportIntentError("Hanya subtitle statis Arial yang didukung Pilot A.")
    if not state.tracks or not any(track.clips for track in state.tracks):
        raise StillExportIntentError("Project belum mempunyai scene gambar untuk diekspor.")
    if any(
        asset.media_type not in {"image", "audio"}
        or (asset.media_type == "image" and asset.has_audio)
        or (
            asset.media_type == "audio"
            and (
                state.narration is None
                or asset.asset_id != state.narration.asset_id
                or Path(asset.path_ref).suffix.lower() != ".wav"
            )
        )
        for asset in state.assets
    ):
        raise StillExportIntentError("Pilot A hanya mendukung gambar dan narasi WAV tunggal.")
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
