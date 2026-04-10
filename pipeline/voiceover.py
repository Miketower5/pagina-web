"""Step 4: ElevenLabs → Voiceover MP3 (guión completo, una sola llamada)."""
import os

from elevenlabs.client import ElevenLabs

from .config import Config


def generate_voiceover(scenes: list[dict], output_dir: str, config: Config) -> str:
    """Concatenate all scene narrations and synthesise a single voiceover MP3.

    A single TTS call is preferred over per-scene calls so that prosody and
    pacing are consistent across the full video.

    Args:
        scenes:     List of scene dicts, each with a "narration" key.
        output_dir: Root output directory for this video job.
        config:     Pipeline configuration (API key, voice, model).

    Returns:
        Absolute path to the saved voiceover MP3 file.
    """
    client = ElevenLabs(api_key=config.elevenlabs_api_key)

    # Join narrations with a short pause marker so the TTS engine breathes
    full_script = "  ".join(scene["narration"] for scene in scenes)

    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    voiceover_path = os.path.join(audio_dir, "voiceover.mp3")

    audio_generator = client.generate(
        text=full_script,
        voice=config.elevenlabs_voice_id,
        model=config.elevenlabs_model,
    )

    with open(voiceover_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    print(f"    voiceover → {voiceover_path}")
    return voiceover_path
