"""Step 6: FFmpeg → Concatenar clips, mezclar voiceover y quemar subtítulos."""
import os
import subprocess

from .config import Config


# ── Internal helpers ──────────────────────────────────────────────────────────

def _run(cmd: list[str]) -> None:
    """Run an FFmpeg command and raise on non-zero exit."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed (exit {result.returncode}):\n{result.stderr}"
        )


def _concat_clips(clip_paths: list[str], output_dir: str) -> str:
    """Concatenate MP4 clips into a single muted video using the concat demuxer."""
    concat_list = os.path.join(output_dir, "concat.txt")
    raw_video = os.path.join(output_dir, "raw_video.mp4")

    with open(concat_list, "w") as f:
        for path in clip_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    _run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_video,
    ])
    return raw_video


# ── Public API ────────────────────────────────────────────────────────────────

def assemble_video(
    clip_paths: list[str],
    voiceover_path: str,
    srt_path: str,
    output_dir: str,
    config: Config,  # noqa: ARG001 — reserved for future resolution/quality flags
) -> str:
    """Produce the final video: clips + voiceover audio + burned-in subtitles.

    Pipeline:
        1. Concatenate all per-scene clips into a single silent video.
        2. Replace the video's audio track with the ElevenLabs voiceover.
        3. Burn the Whisper SRT subtitles into the video using libass.

    Args:
        clip_paths:     Ordered list of per-scene MP4 files (step 3 output).
        voiceover_path: Path to the voiceover MP3 (step 4 output).
        srt_path:       Path to the .srt subtitle file (step 5 output).
        output_dir:     Root output directory for this video job.
        config:         Pipeline configuration.

    Returns:
        Absolute path to the final assembled MP4.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Concatenate silent clips
    raw_video = _concat_clips(clip_paths, output_dir)

    # 2 + 3. Mix audio and burn subtitles in a single FFmpeg pass
    final_path = os.path.join(output_dir, "final_video.mp4")

    # FFmpeg subtitles filter requires forward slashes and escaped colons on
    # all platforms to avoid misinterpreting drive letters as stream selectors.
    srt_escaped = os.path.abspath(srt_path).replace("\\", "/").replace(":", "\\:")

    subtitle_style = (
        "FontSize=22,"
        "PrimaryColour=&H00FFFFFF,"   # white text
        "OutlineColour=&H00000000,"   # black outline
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2"                 # bottom-centre
    )

    _run([
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", voiceover_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", f"subtitles={srt_escaped}:force_style='{subtitle_style}'",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        final_path,
    ])

    print(f"    final video → {final_path}")
    return final_path
