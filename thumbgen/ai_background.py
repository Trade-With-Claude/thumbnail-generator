import base64
import io
import os
from pathlib import Path

import requests
from PIL import Image

from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_URL = "https://api.together.xyz/v1/images/generations"


# Prompt templates per preset
PROMPT_TEMPLATES = {
    "focus": (
        "Dark mysterious {subject}, glowing teal and cyan neural network connections, "
        "dark background, cinematic lighting, digital art, no text, no letters, no words, "
        "16:9 aspect ratio, high detail, futuristic, ADHD focus concentration theme"
    ),
    "sleep": (
        "Dark serene {subject}, glowing deep blue and purple ethereal light, "
        "dark background, peaceful dreamy atmosphere, digital art, no text, no letters, no words, "
        "16:9 aspect ratio, high detail, sleep relaxation theme"
    ),
    "meditation": (
        "Dark spiritual {subject}, glowing purple and golden light energy, "
        "dark background, mystical cosmic atmosphere, digital art, no text, no letters, no words, "
        "16:9 aspect ratio, high detail, meditation healing theme"
    ),
}

# Subject variations based on theme
SUBJECTS = {
    "brain": [
        "human brain silhouette with neural pathways",
        "side profile human head with visible brain and synapses",
        "glowing brain with electric neural connections",
        "human mind visualization with brain waves",
    ],
    "abstract": [
        "cosmic nebula with flowing energy particles",
        "abstract fractal geometry with light streams",
        "aurora borealis over dark landscape",
        "sacred geometry mandala with light rays",
    ],
}


def generate_ai_background(
    title: str,
    preset_name: str = "focus",
    theme: str = "brain",
    size: tuple[int, int] = (1280, 720),
    save_path: str | Path | None = None,
) -> Image.Image:
    """Generate a thumbnail background using Together.ai's Flux model.

    Args:
        title: Video title (used to inform the prompt)
        preset_name: Color preset (focus/sleep/meditation)
        theme: Visual theme (brain/abstract)
        size: Output size
        save_path: Optional path to cache the generated image

    Returns:
        PIL Image ready to be used as background
    """
    if not TOGETHER_API_KEY:
        raise ValueError(
            "TOGETHER_API_KEY not set. Add it to .env file:\n"
            "TOGETHER_API_KEY=your_key_here"
        )

    # Build prompt
    import random
    subjects = SUBJECTS.get(theme, SUBJECTS["brain"])
    subject = random.choice(subjects)
    template = PROMPT_TEMPLATES.get(preset_name, PROMPT_TEMPLATES["focus"])
    prompt = template.format(subject=subject)

    # Add title context to the prompt (without putting text in the image)
    prompt += f", inspired by the concept of {title.lower()}"

    # Call Together.ai API
    response = requests.post(
        TOGETHER_URL,
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "width": 1280,
            "height": 720,
            "steps": 4,
            "n": 1,
            "response_format": "b64_json",
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Together.ai API error ({response.status_code}): {response.text[:200]}")

    data = response.json()
    b64_image = data["data"][0]["b64_json"]

    # Decode image
    image_bytes = base64.b64decode(b64_image)
    img = Image.open(io.BytesIO(image_bytes))

    # Resize to exact dimensions if needed
    if img.size != size:
        img = img.resize(size, Image.LANCZOS)

    # Cache the image if path provided
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path, "PNG")

    return img
