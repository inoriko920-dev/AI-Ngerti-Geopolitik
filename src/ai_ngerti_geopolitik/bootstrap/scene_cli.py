"""Create a genuine image-backed .angproj with explicit per-scene timing, no UI redesign."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.scene_asset_bindings import SceneAssetScanError
from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxFormatError, SceneDocxPlan
from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    build_scene_timeline_review,
    parse_scene_duration_manifest,
    save_reviewed_scene_image_project,
)
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.scene_docx_reader import read_scene_docx
from ai_ngerti_geopolitik.infrastructure.still_frame_preview import (
    StillFramePreviewError,
    render_still_frame,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import (
    StillSequenceExportError,
    export_complete_still_sequence,
    export_still_frame_sequence,
)


def create_scene_project_from_wizard(
    docx: SceneDocxPlan,
    source: Path,
    folder: Path,
    timing: Path,
    destination: Path,
) -> ProjectState:
    """Worker-only finalized import; UI must not guess durations or modify active session."""
    if timing.suffix.lower() != ".txt" or timing.is_symlink():
        raise SceneImportReviewError("pilih TXT durasi yang valid")
    if not 0 < timing.stat().st_size <= 256_000:
        raise SceneImportReviewError("TXT durasi terlalu besar atau kosong")
    text = timing.read_text(encoding="utf-8-sig")
    fps_labels = [
        match.group(1)
        for line in text.splitlines()
        if (match := re.fullmatch(r"#\s*FPS\s+project:\s*(30|60)\s*", line.strip(), re.I))
    ]
    if len(fps_labels) != 1:
        raise SceneImportReviewError("TXT durasi wajib memiliki satu '# FPS project: 30' atau 60")
    fps = int(fps_labels[0])
    frames = parse_scene_duration_manifest(text, scene_count=len(docx.scenes))
    inventory = scan_scene_asset_folder(docx, folder)
    review = build_scene_timeline_review(docx, inventory, frames, fps=fps)
    fingerprints = verify_scene_image_media(inventory)
    return save_reviewed_scene_image_project(
        docx,
        source,
        folder,
        review,
        fingerprints,
        destination,
        project_id=f"SCENE-{uuid4().hex}",
        project_name=destination.stem,
        repository=JsonProjectRepository(),
        read_docx=read_scene_docx,
        scan=scan_scene_asset_folder,
        verify=verify_scene_image_media,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Impor Scene DOCX dan gambar Axxx tanpa mengubah UI atau menjalankan render."
    )
    modes = parser.add_subparsers(dest="action", required=True)
    template = modes.add_parser("template", help="Buat TXT durasi kosong untuk setiap scene.")
    template.add_argument("--docx", required=True)
    template.add_argument("--output", required=True)
    template.add_argument("--fps", type=int, choices=(30, 60), default=30)

    create = modes.add_parser("create", help="Buat project .angproj dari durasi eksplisit.")
    create.add_argument("--docx", required=True)
    create.add_argument("--assets", required=True)
    create.add_argument("--timing", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--name", required=True)
    create.add_argument("--fps", type=int, choices=(30, 60), default=30)

    preview = modes.add_parser("preview", help="Simpan satu frame preview gambar sebagai PNG.")
    preview.add_argument("--project", required=True)
    preview.add_argument("--frame", type=int, required=True)
    preview.add_argument("--output", required=True)

    frame_parser = modes.add_parser(
        "frames", help="Ekspor PNG frame sequence dan manifest, bukan MP4."
    )
    frame_parser.add_argument("--project", required=True)
    frame_parser.add_argument("--start", required=True, type=int)
    frame_parser.add_argument("--count", required=True, type=int)
    frame_parser.add_argument("--output", required=True)

    full_parser = modes.add_parser(
        "frames-all", help="Ekspor seluruh timeline gambar sebagai batch PNG, bukan MP4."
    )
    full_parser.add_argument("--project", required=True)
    full_parser.add_argument("--output", required=True)
    full_parser.add_argument("--batch-size", type=int, default=300)

    args = parser.parse_args(argv)
    try:
        if args.action == "frames-all":
            state = JsonProjectRepository().load(Path(args.project))
            export_complete_still_sequence(state, Path(args.output), batch_size=args.batch_size)
            print(
                f"Berhasil ekspor {state.timeline_end_frame} frame PNG "
                "dalam batch. Ini bukan MP4 dan tidak memuat audio."
            )
            return 0
        if args.action == "frames":
            state = JsonProjectRepository().load(Path(args.project))
            export_still_frame_sequence(
                state, Path(args.output), start_frame=args.start, count=args.count
            )
            print(f"Berhasil mengekspor {args.count} frame PNG. Ini bukan video MP4.")
            return 0
        if args.action == "preview":
            target = Path(args.output)
            if target.suffix.lower() != ".png":
                raise SceneImportReviewError("preview output must be PNG")
            if target.exists():
                raise SceneImportReviewError("preview destination already exists")
            state = JsonProjectRepository().load(Path(args.project))
            image = render_still_frame(state, args.frame)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise SceneImportReviewError("preview destination already exists")
            if not image.save(str(target)):
                raise SceneImportReviewError("preview image could not be saved")
            print(f"Preview frame {args.frame} tersimpan sebagai PNG.")
            return 0
        source = Path(args.docx)
        docx = read_scene_docx(source)
        if args.action == "template":
            target = Path(args.output)
            if target.suffix.lower() != ".txt":
                raise SceneImportReviewError("template must use .txt")
            text = (
                f"# FPS project: {args.fps}\n"
                "# Contoh: Scene 1: 150 frames berarti 5 detik pada 30 FPS.\n"
                "# Isi seluruh ____ dengan durasi positif dalam jumlah frame.\n"
                + "".join(f"Scene {row.number}: ____ frames\n" for row in docx.scenes)
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            print(f"Template dibuat untuk {len(docx.scenes)} scene. Isi durasinya dahulu.")
            return 0

        duration_text = Path(args.timing).read_text(encoding="utf-8-sig")
        frames = parse_scene_duration_manifest(duration_text, scene_count=len(docx.scenes))
        inventory = scan_scene_asset_folder(docx, Path(args.assets))
        review = build_scene_timeline_review(docx, inventory, frames, fps=args.fps)
        verified = verify_scene_image_media(inventory)
        project = save_reviewed_scene_image_project(
            docx,
            source,
            Path(args.assets),
            review,
            verified,
            Path(args.output),
            project_id=f"SCENE-{uuid4().hex}",
            project_name=args.name,
            repository=JsonProjectRepository(),
            read_docx=read_scene_docx,
            scan=scan_scene_asset_folder,
            verify=verify_scene_image_media,
        )
        print(
            f"Project tersimpan: {len(review.scenes)} scene, {len(project.assets)} aset, "
            f"{review.total_frames} frame. Frame preview tersedia; "
            "animasi dan MP4 belum dikualifikasi."
        )
        return 0
    except (
        SceneDocxFormatError,
        SceneImportReviewError,
        SceneAssetScanError,
        StillFramePreviewError,
        StillSequenceExportError,
        OSError,
        ValueError,
    ) as err:
        # Reader errors are redacted. Do not print user's private input paths.
        print(f"GAGAL: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
