"""Create a genuine image-backed .angproj with explicit per-scene timing, no UI redesign."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.scene_asset_bindings import SceneAssetScanError
from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxFormatError
from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    build_scene_timeline_review,
    parse_scene_duration_manifest,
    save_reviewed_scene_image_project,
)
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

    args = parser.parse_args(argv)
    try:
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
        OSError,
        ValueError,
    ) as err:
        # Reader errors are redacted. Do not print user's private input paths.
        print(f"GAGAL: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
