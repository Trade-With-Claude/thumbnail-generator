from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from thumbgen.config import load_brand_config, get_preset


def render_thumbnail(
    title: str,
    preset_name: str = "focus",
    output_path: str | Path = "output/thumbnail.png",
    config: dict | None = None,
) -> Path:
    """Render a thumbnail with text effects, vignette, and gradient overlay.

    Pipeline: dark canvas → gradient overlay → vignette → text (shadow → glow → main)
    """
    # Lazy imports to avoid circular dependency
    from thumbgen.text import draw_title
    from thumbgen.effects import apply_vignette, apply_gradient_overlay

    if config is None:
        config = load_brand_config()

    preset = get_preset(config, preset_name)
    canvas_cfg = config["canvas"]
    font_cfg = config["font"]
    layout_cfg = config["layout"]
    effects_cfg = config["effects"]

    width = canvas_cfg["width"]
    height = canvas_cfg["height"]

    # 1. Create dark canvas with preset tint
    bg_color = _hex_to_rgb(preset["background_tint"])
    img = Image.new("RGB", (width, height), bg_color)

    # 2. Apply gradient overlay (subtle colored gradient from bottom)
    if effects_cfg.get("gradient_overlay", False):
        img = apply_gradient_overlay(
            img,
            color=preset["accent"],
            opacity=0.15,
            direction="bottom",
        )

    # 3. Apply vignette (darken edges)
    if effects_cfg.get("vignette", False):
        strength = effects_cfg.get("vignette_strength", 0.6)
        img = apply_vignette(img, strength=strength)

    # 4. Prepare text and font
    text = title.upper() if font_cfg.get("style") == "uppercase" else title
    font_size = font_cfg.get("primary_size", 90)
    font = _load_font(font_cfg.get("family", ""), font_size)

    # Calculate text position
    margin = layout_cfg.get("text_safe_margin", 80)
    max_width = width - margin * 2

    # Auto-size: shrink font if text is too wide
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    while text_width > max_width and font_size > 30:
        font_size -= 4
        font = _load_font(font_cfg.get("family", ""), font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]

    # Center position (shifted up slightly from dead center)
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 40

    # 5. Draw text with effects (shadow → glow → main text)
    img = draw_title(img, text, font, (x, y), config, preset)

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")

    return output_path


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _load_font(family: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a font by family name, fall back to default."""
    font_paths = [
        f"fonts/{family}.ttf",
        f"fonts/{family}.otf",
        f"/System/Library/Fonts/{family}.ttf",
        f"/System/Library/Fonts/Supplemental/{family}.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue

    try:
        return ImageFont.truetype(family, size)
    except (OSError, IOError):
        pass

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()
