"""Explicit W5 per-word timing boundary.

This module deliberately separates deterministic timing convenience from speech
alignment. It does not perform ASR, transcription, phoneme analysis, or audio
alignment.
"""

from __future__ import annotations

from ai_ngerti_geopolitik.domain import FrameTime, SubtitleCue, WordTiming

NOT_SPEECH_ALIGNMENT_LABEL = "NOT speech alignment"


class WordTimingBoundaryError(ValueError):
    pass


def evenly_distribute_words_not_speech_alignment(
    cue: SubtitleCue,
    *,
    acknowledge_not_speech_alignment: bool,
) -> tuple[WordTiming, ...]:
    """Deterministically distribute written words across a cue.

    The caller must explicitly acknowledge that this is NOT speech alignment.
    """

    if not acknowledge_not_speech_alignment:
        raise WordTimingBoundaryError(
            "even word timing requires explicit acknowledgement: NOT speech alignment"
        )

    words = cue.text.split()
    if not words:
        raise WordTimingBoundaryError("subtitle cue has no words to distribute")

    duration = cue.end.frames - cue.start.frames
    if duration < len(words):
        raise WordTimingBoundaryError(
            "subtitle cue is too short to allocate at least one frame per word"
        )

    timings: list[WordTiming] = []
    for index, word in enumerate(words):
        start_frame = cue.start.frames + (duration * index) // len(words)
        end_frame = cue.start.frames + (duration * (index + 1)) // len(words)
        timings.append(
            WordTiming(
                word_id=f"{cue.cue_id}-W{index + 1:03d}",
                word=word,
                start=FrameTime(start_frame, cue.start.fps),
                end=FrameTime(end_frame, cue.start.fps),
            )
        )
    return tuple(timings)
