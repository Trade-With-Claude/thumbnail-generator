from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from thumbgen.config import load_brand_config, get_preset


def render_thumbnail(
    title: str,
    preset_name: str = "focus",
    output_path: str | Path = "output/thumbnail.png",
    config: dict | None = None,
) -> Path:
    """Render a basic thumbnail with title text on a dark canvas.

    Args:
        title: The text to display (will be uppercased)
        preset_name: Color preset from brand.json (focus, sleep, meditation)
        output_path: Where to save the PNG
        config: Brand config dict (loaded from brand.json if None)

    Returns:
        Path to the saved thumbnail
    """
    if config is None:
        config = load_brand_config()

    preset = get_preset(config, preset_name)
    canvas_cfg = config["canvas"]
    font_cfg = config["font"]
    layout_cfg = config["layout"]

    width = canvas_cfg["width"]
    height = canvas_cfg["height"]

    # Create dark canvas with preset tint
    bg_color = _hex_to_rgb(preset["background_tint"])
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Prepare text
    text = title.upper() if font_cfg.get("style") == "uppercase" else title

    # Load font — try system font, fall back to Pillow default
    font_size = font_cfg.get("primary_size", 90)
    font = _load_font(font_cfg.get("family", ""), font_size)

    # Calculate text position (centered)
    margin = layout_cfg.get("text_safe_margin", 80)
    max_width = width - margin * 2

    # Auto-size: shrink font if text is too wide
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    while text_width > max_width and font_size > 30:
        font_size -= 4
        font = _load_font(font_cfg.get("family", ""), font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]

    # Center position
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 40  # Shift up slightly from dead center

    # Draw text
    text_color = _hex_to_rgb(font_cfg.get("color", "#FFFFFF"))
    draw.text((x, y), text, font=font, fill=text_color)

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
    # Try common font paths
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

    # Try system font by name
    try:
        return ImageFont.truetype(family, size)
    except (OSError, IOError):
        pass

    # Fall back to Pillow's default — load_default with size
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Older Pillow versions don't support size param
        return ImageFont.load_default()
