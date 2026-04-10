"""Step 2: Imagen 3 → Una imagen por escena (9:16, vertical)."""
import os

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from .config import Config

_IMAGEN_MODEL = "imagen-3.0-generate-001"


def generate_images(scenes: list[dict], output_dir: str, config: Config) -> list[str]:
    """Generate one 9:16 image per scene using Imagen 3 on Vertex AI.

    Args:
        scenes:     List of scene dicts from the script generator.
        output_dir: Root output directory for this video job.
        config:     Pipeline configuration.

    Returns:
        Ordered list of absolute paths to the saved PNG files.
    """
    vertexai.init(project=config.google_project_id, location=config.google_location)
    model = ImageGenerationModel.from_pretrained(_IMAGEN_MODEL)

    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    image_paths: list[str] = []

    for scene in scenes:
        scene_num = scene["scene_number"]
        prompt = scene["visual_prompt"]

        result = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="9:16",
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )

        path = os.path.join(images_dir, f"scene_{scene_num:02d}.png")
        result[0].save(location=path)
        image_paths.append(path)
        print(f"    scene {scene_num:02d} → {path}")

    return image_paths
