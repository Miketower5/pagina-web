"""Step 5: Whisper API → Subtítulos .SRT sincronizados con el voiceover."""
import os

from openai import OpenAI

from .config import Config


def generate_subtitles(voiceover_path: str, output_dir: str, config: Config) -> str:
    """Transcribe the voiceover MP3 with Whisper and save a .srt subtitle file.

    Whisper returns word-level timestamps when response_format="srt", which
    produces subtitles that are tightly synchronised with the narration.

    Args:
        voiceover_path: Absolute path to the voiceover MP3 produced by step 4.
        output_dir:     Root output directory for this video job.
        config:         Pipeline configuration (OpenAI API key).

    Returns:
        Absolute path to the saved .srt file.
    """
    client = OpenAI(api_key=config.openai_api_key)

    srt_path = os.path.join(output_dir, "subtitles.srt")

    with open(voiceover_path, "rb") as audio_file:
        srt_content = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt",
        )

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"    subtitles → {srt_path}")
    return srt_path
