"""Step 3: Veo 2 → Video clip por escena (image-to-video, 9:16)."""
import os
import time

import vertexai
from vertexai.preview.vision_models import Image, VideoGenerationModel

from .config import Config

_VEO_MODEL = "veo-2.0-generate-001"
_POLL_INTERVAL = 10  # seconds between status checks


def generate_video_clips(
    scenes: list[dict],
    image_paths: list[str],
    output_dir: str,
    config: Config,
) -> list[str]:
    """Animate each Imagen 3 image into a short video clip using Veo 2.

    Veo 2 is called in image-to-video mode: the reference image anchors the
    first frame and the visual prompt drives camera motion and action.

    Args:
        scenes:      List of scene dicts (must have scene_number, visual_prompt).
        image_paths: Ordered list of PNG paths produced by image_generator.
        output_dir:  Root output directory for this video job.
        config:      Pipeline configuration.

    Returns:
        Ordered list of absolute paths to the saved MP4 clip files.
    """
    vertexai.init(project=config.google_project_id, location=config.google_location)
    model = VideoGenerationModel.from_pretrained(_VEO_MODEL)

    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    clip_paths: list[str] = []

    for scene, image_path in zip(scenes, image_paths):
        scene_num = scene["scene_number"]
        prompt = scene["visual_prompt"]

        reference_image = Image.load_from_file(image_path)

        operation = model.generate_video(
            prompt=prompt,
            image=reference_image,
            duration_seconds=config.clip_duration,
            aspect_ratio="9:16",
        )

        # Poll until the long-running operation completes
        while not operation.done():
            time.sleep(_POLL_INTERVAL)

        clip_path = os.path.join(clips_dir, f"clip_{scene_num:02d}.mp4")
        operation.result().videos[0].save(clip_path)
        clip_paths.append(clip_path)
        print(f"    scene {scene_num:02d} → {clip_path}")

    return clip_paths
