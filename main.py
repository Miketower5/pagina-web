"""Video creation pipeline — entry point.

Usage:
    python main.py "10 curiosidades sobre los pulpos"
    python main.py "The history of coffee" --no-publish
    python main.py "Por qué el cielo es azul" --scenes 7 --clip-duration 6
"""
import argparse
import json
import os

from dotenv import load_dotenv

from pipeline.assembler import assemble_video
from pipeline.config import Config
from pipeline.image_generator import generate_images
from pipeline.publisher import publish_tiktok, publish_youtube
from pipeline.script_generator import generate_script
from pipeline.subtitles import generate_subtitles
from pipeline.video_generator import generate_video_clips
from pipeline.voiceover import generate_voiceover


def load_config(args: argparse.Namespace) -> Config:
    load_dotenv()
    return Config(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        claude_model=os.getenv("CLAUDE_MODEL", "claude-opus-4-6"),
        google_project_id=os.getenv("GOOGLE_PROJECT_ID", ""),
        google_location=os.getenv("GOOGLE_LOCATION", "us-central1"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        elevenlabs_model=os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        tiktok_client_key=os.getenv("TIKTOK_CLIENT_KEY", ""),
        tiktok_client_secret=os.getenv("TIKTOK_CLIENT_SECRET", ""),
        tiktok_access_token=os.getenv("TIKTOK_ACCESS_TOKEN", ""),
        youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
        youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        youtube_refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        scenes_count=args.scenes or int(os.getenv("SCENES_COUNT", "5")),
        clip_duration=args.clip_duration or int(os.getenv("CLIP_DURATION", "5")),
    )


def run_pipeline(topic: str, config: Config, publish: bool = True) -> dict:
    """Execute all seven pipeline steps in sequence and return a results dict."""
    # Each job gets its own subdirectory so runs never clobber each other
    safe_topic = topic[:40].replace(" ", "_").replace("/", "-")
    output_dir = os.path.join(config.output_dir, safe_topic)
    os.makedirs(output_dir, exist_ok=True)

    results: dict = {}

    _header(f"VIDEO CREATION PIPELINE\nTopic: {topic}")

    # ── Step 1: Script ──────────────────────────────────────────────────────
    _step(1, 7, "Generating script with Claude")
    script = generate_script(topic, config)
    script_path = os.path.join(output_dir, "script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
    results["script"] = script_path
    print(f"  Title   : {script['title']}")
    print(f"  Scenes  : {len(script['scenes'])}")

    # ── Step 2: Images ──────────────────────────────────────────────────────
    _step(2, 7, "Generating images with Imagen 3")
    image_paths = generate_images(script["scenes"], output_dir, config)
    results["images"] = image_paths

    # ── Step 3: Video clips ─────────────────────────────────────────────────
    _step(3, 7, "Generating video clips with Veo 2")
    clip_paths = generate_video_clips(script["scenes"], image_paths, output_dir, config)
    results["clips"] = clip_paths

    # ── Step 4: Voiceover ───────────────────────────────────────────────────
    _step(4, 7, "Generating voiceover with ElevenLabs")
    voiceover_path = generate_voiceover(script["scenes"], output_dir, config)
    results["voiceover"] = voiceover_path

    # ── Step 5: Subtitles ───────────────────────────────────────────────────
    _step(5, 7, "Transcribing subtitles with Whisper")
    srt_path = generate_subtitles(voiceover_path, output_dir, config)
    results["subtitles"] = srt_path

    # ── Step 6: Assemble ────────────────────────────────────────────────────
    _step(6, 7, "Assembling final video with FFmpeg")
    final_video = assemble_video(clip_paths, voiceover_path, srt_path, output_dir, config)
    results["final_video"] = final_video

    # ── Step 7: Publish ─────────────────────────────────────────────────────
    _step(7, 7, "Publishing" if publish else "Publishing (skipped)")
    if publish:
        results["youtube_url"] = publish_youtube(final_video, script, config)
        results["tiktok_publish_id"] = publish_tiktok(final_video, script, config)
    else:
        print("  Skipped — pass without --no-publish to upload.")

    # Persist results
    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    _header("PIPELINE COMPLETE")
    print(f"  Output : {output_dir}")
    if "youtube_url" in results:
        print(f"  YouTube: {results['youtube_url']}")

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def _header(text: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n {text}\n{bar}")


def _step(n: int, total: int, label: str) -> None:
    print(f"\n[{n}/{total}] {label}...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-powered short video creation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("topic", help="Topic or idea for the video")
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip TikTok / YouTube upload (produce files only)",
    )
    parser.add_argument(
        "--scenes",
        type=int,
        default=None,
        help="Number of scenes (overrides SCENES_COUNT env var)",
    )
    parser.add_argument(
        "--clip-duration",
        type=int,
        default=None,
        dest="clip_duration",
        help="Seconds per Veo 2 clip (overrides CLIP_DURATION env var)",
    )

    args = parser.parse_args()
    config = load_config(args)
    run_pipeline(args.topic, config, publish=not args.no_publish)


if __name__ == "__main__":
    main()
