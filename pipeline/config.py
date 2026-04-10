"""Pipeline configuration loaded from environment variables."""
from dataclasses import dataclass, field


@dataclass
class Config:
    # ── Claude API ──────────────────────────────────────────────────────────
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-6"

    # ── Google Cloud (Imagen 3 + Veo 2 via Vertex AI) ──────────────────────
    google_project_id: str = ""
    google_location: str = "us-central1"

    # ── ElevenLabs ──────────────────────────────────────────────────────────
    elevenlabs_api_key: str = ""
    # Default: Rachel voice (multilingual)
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_multilingual_v2"

    # ── OpenAI (Whisper) ────────────────────────────────────────────────────
    openai_api_key: str = ""

    # ── TikTok Content Posting API ──────────────────────────────────────────
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_access_token: str = ""

    # ── YouTube Data API v3 ─────────────────────────────────────────────────
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_refresh_token: str = ""

    # ── Pipeline settings ───────────────────────────────────────────────────
    output_dir: str = "output"
    scenes_count: int = 5
    # Seconds per Veo 2 clip (5–8 s recommended)
    clip_duration: int = 5
    # Vertical 9:16 for TikTok / YouTube Shorts
    video_width: int = 1080
    video_height: int = 1920
