"""Step 1: Claude API → Idea + guión + prompts visuales por escena."""
import json

import anthropic

from .config import Config

_SYSTEM_PROMPT = """\
You are a creative director specialising in short-form vertical video for TikTok and YouTube Shorts.

Given a topic you will produce:
  1. A compelling video concept
  2. A narration script split into exactly N scenes (each ~5 seconds when spoken)
  3. A detailed image/video generation prompt for each scene

Return ONLY a valid JSON object — no markdown fences, no extra text — with this schema:

{
  "title": "<catchy title, max 100 chars>",
  "description": "<one-sentence description for social media>",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "scenes": [
    {
      "scene_number": 1,
      "narration": "<spoken text for this scene, ~20 words>",
      "visual_prompt": "<rich cinematic prompt for image/video generation, 50-80 words>",
      "duration": 5
    }
  ]
}
"""


def generate_script(topic: str, config: Config) -> dict:
    """Call Claude to generate a full video script with per-scene visual prompts.

    Args:
        topic: Free-text description of the video topic or idea.
        config: Pipeline configuration (API key, model, scene count).

    Returns:
        Parsed JSON dict matching the schema in _SYSTEM_PROMPT.
    """
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    message = client.messages.create(
        model=config.claude_model,
        max_tokens=2048,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create a {config.scenes_count}-scene short video about: {topic}\n\n"
                    "Each scene narration must be concise (fits ~5 seconds of speech). "
                    "Visual prompts must be highly descriptive and cinematic."
                ),
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences if the model includes them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
