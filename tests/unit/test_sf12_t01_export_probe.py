from ai_ngerti_geopolitik.application.export_capabilities import (
    ExportCapabilities,
    ExportToolchain,
)
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import (
    detect_export_toolchain,
)


def test_no_tools_fail_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        "ai_ngerti_geopolitik.infrastructure.export_capability_probe.shutil.which",
        lambda _name: None,
    )
    assert not detect_export_toolchain().baseline_detected


def test_present_encoders_do_not_imply_export_dispatch() -> None:
    def runner(argv: tuple[str, ...]) -> tuple[int, str]:
        if argv[-1] == "-version":
            return 0, "ffprobe"
        return 0, " V....D libx264\n V....D libx265\n A..... aac"

    toolchain = detect_export_toolchain(
        ffmpeg_binary="fixture-ffmpeg",
        ffprobe_binary="fixture-ffprobe",
        runner=runner,
    )
    assert toolchain.baseline_detected
    assert toolchain.h265_encoder_found
    assert not ExportCapabilities(toolchain=toolchain).can_start_render
    assert not ExportCapabilities(
        toolchain=toolchain, h264_export_qualified=True
    ).can_start_render
    assert not ExportCapabilities(
        toolchain=toolchain, render_handler_wired=True
    ).can_start_render


def test_probe_failure_and_malformed_encoder_flags_are_safe() -> None:
    def runner(argv: tuple[str, ...]) -> tuple[int, str]:
        return (1, "") if argv[-1] == "-version" else (0, "libx264 aac")

    toolchain = detect_export_toolchain(
        ffmpeg_binary="fixture-ffmpeg",
        ffprobe_binary="fixture-ffprobe",
        runner=runner,
    )
    assert not toolchain.baseline_detected
    assert not toolchain.h264_encoder_found
    assert not toolchain.aac_encoder_found


def test_timeout_and_missing_audio_keep_baseline_off() -> None:
    toolchain = detect_export_toolchain(
        ffmpeg_binary="fixture-ffmpeg",
        ffprobe_binary="fixture-ffprobe",
        runner=lambda _argv: None,
    )
    assert not toolchain.baseline_detected
    assert not ExportToolchain(
        ffmpeg_found=True,
        ffprobe_found=True,
        h264_encoder_found=True,
    ).baseline_detected
