from ai_ngerti_geopolitik.domain import (
    AudioProperties,
    Clip,
    ClipProperties,
    ColorProperties,
    FrameTime,
    SpeedProperties,
    VideoProperties,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_properties import (
    atempo_chain,
    build_w3_filter_plan,
)


def _clip() -> Clip:
    return Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(120, 30),
        properties=ClipProperties(
            video=VideoProperties(
                position_x=20,
                position_y=-10,
                scale_x_percent=80,
                scale_y_percent=75,
                rotation_tenths=100,
                opacity_percent=75,
                crop_left_percent=5,
                crop_top_percent=4,
                crop_right_percent=3,
                crop_bottom_percent=2,
            ),
            audio=AudioProperties(
                volume_percent=70,
                pan_percent=-25,
                fade_in_frames=15,
                fade_out_frames=30,
            ),
            color=ColorProperties(
                brightness_percent=10,
                exposure_tenths_ev=5,
                contrast_percent=20,
                saturation_percent=30,
                temperature_percent=10,
                tint_percent=-6,
            ),
            speed=SpeedProperties(200),
        ),
    )


def test_filter_plan_covers_w3_property_groups() -> None:
    clip = _clip()
    plan = build_w3_filter_plan(clip, 30)
    video = ",".join(plan.video_filters)
    audio = ",".join(plan.audio_filters)

    assert "crop=" in video
    assert "scale=" in video
    assert "rotate=" in video
    assert "eq=" in video
    assert "colorbalance=" in video
    assert "colorchannelmixer=aa=0.75" in video
    assert plan.overlay_x.endswith("+20")
    assert plan.overlay_y.endswith("+-10")

    assert "atempo=2" in audio
    assert "volume=0.7" in audio
    assert "pan=stereo" in audio
    assert "afade=t=in" in audio
    assert "afade=t=out" in audio
    assert plan.duration_seconds == 2.0


def test_atempo_chain_handles_full_w3_speed_range() -> None:
    assert atempo_chain(25) == (0.5, 0.5)
    assert atempo_chain(50) == (0.5,)
    assert atempo_chain(100) == (1.0,)
    assert atempo_chain(200) == (2.0,)
    assert atempo_chain(400) == (2.0, 2.0)
