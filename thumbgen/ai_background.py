import base64
import hashlib
import io
import os
import random
from pathlib import Path

import requests
from PIL import Image

from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_URL = "https://api.together.xyz/v1/images/generations"

# Cache directory for AI-generated backgrounds
CACHE_DIR = Path(__file__).parent.parent / "themes" / "ai_cache"


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
        "human brain silhouette made of glowing neural network nodes and connections",
        "side profile human head with visible brain made of interconnected glowing dots and lines",
        "glowing brain with dense network of synaptic connections and electric pulses",
        "human mind visualization with intricate web of neural pathways and tiny bright nodes",
        "brain composed of thousands of connected glowing dots forming neural network pattern",
        "wireframe brain structure with pulsing network connections between nodes",
    ],
    "abstract": [
        "vast network of interconnected glowing nodes floating in space",
        "cosmic nebula with flowing energy particles and network connections",
        "abstract digital network grid with glowing intersection points",
        "sacred geometry mandala with interconnected light nodes",
        "deep space scene with constellation-like network of bright connected dots",
        "flowing particle network with organic connections and light trails",
    ],
}


def generate_ai_background(
    title: str,
    preset_name: str = "focus",
    theme: str = "brain",
    size: tuple[int, int] = (1280, 720),
) -> Image.Image:
    """Generate a thumbnail background using Together.ai's Flux model.

    Generated images are cached in themes/ai_cache/ so they can be reused.
    """
    if not TOGETHER_API_KEY:
        raise ValueError(
            "TOGETHER_API_KEY not set. Add it to .env file:\n"
            "TOGETHER_API_KEY=your_key_here"
        )

    # Build prompt
    subjects = SUBJECTS.get(theme, SUBJECTS["brain"])
    subject = random.choice(subjects)
    template = PROMPT_TEMPLATES.get(preset_name, PROMPT_TEMPLATES["focus"])
    prompt = template.format(subject=subject)

    # Add title context to the prompt (without putting text in the image)
    prompt += f", inspired by the concept of {title.lower()}"

    # Generate a cache filename from the prompt
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:10]
    safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
    cache_filename = f"{safe_title}_{preset_name}_{theme}_{prompt_hash}.png"
    cache_path = CACHE_DIR / cache_filename

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

    # Always cache the generated background
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(cache_path, "PNG")

    return img


def list_cached_backgrounds() -> list[Path]:
    """List all cached AI-generated backgrounds."""
    if not CACHE_DIR.exists():
        return []
    return sorted(CACHE_DIR.glob("*.png"))


def get_cached_background(preset_name: str = None, theme: str = None) -> Image.Image | None:
    """Get a random cached background, optionally filtered by preset/theme."""
    cached = list_cached_backgrounds()
    if not cached:
        return None

    # Filter by preset/theme if specified
    if preset_name:
        cached = [p for p in cached if preset_name in p.name] or cached
    if theme:
        cached = [p for p in cached if theme in p.name] or cached

    path = random.choice(cached)
    return Image.open(path)
