import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from thumbgen.renderer import _hex_to_rgb


# Theme directories
THEMES_DIR = Path(__file__).parent.parent / "themes"


def load_theme_background(
    theme_name: str,
    preset: dict,
    size: tuple[int, int] = (1280, 720),
    seed: int | None = None,
) -> Image.Image:
    """Load or generate a theme background.

    If a custom image exists in themes/{name}/, uses it.
    Otherwise generates a procedural background.
    """
    theme_dir = THEMES_DIR / theme_name

    # Check for pre-made images
    if theme_dir.exists():
        images = list(theme_dir.glob("*.png")) + list(theme_dir.glob("*.jpg"))
        if images:
            img = Image.open(random.choice(images))
            return img.resize(size, Image.LANCZOS)

    # Generate procedurally
    if theme_name == "brain":
        return _generate_brain_theme(size, preset, seed)
    elif theme_name == "abstract":
        return _generate_abstract_theme(size, preset, seed)
    else:
        return _generate_abstract_theme(size, preset, seed)


def load_custom_background(path: str | Path, size: tuple[int, int] = (1280, 720)) -> Image.Image:
    """Load a custom background image and resize to thumbnail dimensions."""
    img = Image.open(path)
    return img.resize(size, Image.LANCZOS)


def blend_background(
    base: Image.Image,
    background: Image.Image,
    opacity: float = 0.7,
) -> Image.Image:
    """Blend a background image onto a dark base with given opacity."""
    base = base.convert("RGBA")
    bg = background.convert("RGBA")

    # Apply opacity to the background
    r, g, b, a = bg.split()
    a = a.point(lambda x: int(x * opacity))
    bg = Image.merge("RGBA", (r, g, b, a))

    return Image.alpha_composite(base, bg).convert("RGB")


def _generate_brain_theme(
    size: tuple[int, int],
    preset: dict,
    seed: int | None = None,
) -> Image.Image:
    """Generate a brain/neural network themed background.

    Creates an abstract neural pattern with nodes and connections.
    """
    if seed is not None:
        random.seed(seed)

    width, height = size
    accent = _hex_to_rgb(preset["accent"])
    secondary = _hex_to_rgb(preset["accent_secondary"])
    bg_tint = _hex_to_rgb(preset["background_tint"])

    img = Image.new("RGBA", size, (*bg_tint, 255))
    draw = ImageDraw.Draw(img)

    # Generate neural nodes
    nodes = []
    for _ in range(60):
        x = random.randint(0, width)
        y = random.randint(0, height)
        nodes.append((x, y))

    # Draw connections between nearby nodes (neural pathways)
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i >= j:
                continue
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if dist < 250:
                alpha = int(max(0, (1 - dist / 250)) * 80)
                line_color = (*accent, alpha)
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # Draw nodes (synapses)
    for x, y in nodes:
        r = random.randint(2, 6)
        glow_r = r * 4
        # Glow
        for gr in range(glow_r, r, -1):
            alpha = int((1 - gr / glow_r) * 40)
            color = (*accent, alpha)
            draw.ellipse([x - gr, y - gr, x + gr, y + gr], fill=color)
        # Core
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(*accent, 200))

    # Add a central brain-like circular structure
    cx, cy = width // 2 + random.randint(-100, 100), height // 2 + random.randint(-50, 50)
    for ring in range(3):
        radius = 120 + ring * 50
        alpha = 40 - ring * 10
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            wobble = random.uniform(0.9, 1.1)
            px = cx + int(radius * wobble * math.cos(rad))
            py = cy + int(radius * wobble * math.sin(rad) * 0.7)  # Elliptical
            dot_r = 1
            draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r],
                         fill=(*secondary, alpha))

    # Light blur for slight softness (keep it crisp)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Add some bright accent particles
    particle_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(particle_layer)
    for _ in range(30):
        px = random.randint(0, width)
        py = random.randint(0, height)
        pr = random.randint(1, 3)
        pdraw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(*secondary, 150))

    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, particle_layer)

    return img


def _generate_abstract_theme(
    size: tuple[int, int],
    preset: dict,
    seed: int | None = None,
) -> Image.Image:
    """Generate an abstract/cosmic themed background.

    Creates flowing gradients, aurora-like streaks, and soft particles.
    """
    if seed is not None:
        random.seed(seed)

    width, height = size
    accent = _hex_to_rgb(preset["accent"])
    secondary = _hex_to_rgb(preset["accent_secondary"])
    bg_tint = _hex_to_rgb(preset["background_tint"])

    img = Image.new("RGBA", size, (*bg_tint, 255))
    draw = ImageDraw.Draw(img)

    # Aurora-like horizontal streaks
    for _ in range(5):
        y_center = random.randint(height // 4, height * 3 // 4)
        streak_height = random.randint(60, 150)
        color = accent if random.random() > 0.4 else secondary

        for dy in range(streak_height):
            y = y_center + dy - streak_height // 2
            if 0 <= y < height:
                # Fade from center
                dist_from_center = abs(dy - streak_height // 2) / (streak_height // 2)
                alpha = int((1 - dist_from_center ** 2) * 35)
                # Wavy x offset
                wave = int(math.sin(y * 0.02 + random.random() * 6) * 80)
                x_start = max(0, wave + random.randint(-100, 100))
                x_end = min(width, x_start + random.randint(400, width))
                draw.line([(x_start, y), (x_end, y)], fill=(*color, alpha))

    # Light blur for smooth aurora effect (reduced for crispness)
    img = img.filter(ImageFilter.GaussianBlur(radius=3))

    # Floating particles / stars
    particle_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(particle_layer)

    for _ in range(80):
        px = random.randint(0, width)
        py = random.randint(0, height)
        pr = random.uniform(0.5, 3)
        brightness = random.randint(100, 255)
        color = (*accent, brightness) if random.random() > 0.3 else (255, 255, 255, brightness)
        pdraw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=color)

    # Some larger glowing orbs
    for _ in range(4):
        ox = random.randint(width // 4, width * 3 // 4)
        oy = random.randint(height // 4, height * 3 // 4)
        orb_r = random.randint(30, 80)
        orb_color = accent if random.random() > 0.5 else secondary
        for r in range(orb_r, 0, -2):
            alpha = int((1 - r / orb_r) * 20)
            pdraw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(*orb_color, alpha))

    particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.alpha_composite(img, particle_layer)

    return img
