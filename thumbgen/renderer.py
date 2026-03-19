from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from thumbgen.config import load_brand_config, get_preset


def render_thumbnail(
    title: str,
    preset_name: str = "focus",
    output_path: str | Path = "output/thumbnail.png",
    config: dict | None = None,
    theme: str | None = None,
    background: str | None = None,
    seed: int | None = None,
) -> Path:
    """Render a thumbnail with theme background, text effects, vignette, and gradient.

    Pipeline: dark canvas → theme/background → gradient overlay → vignette → text
    """
    from thumbgen.text import draw_title
    from thumbgen.effects import apply_vignette, apply_gradient_overlay
    from thumbgen.themes import load_theme_background, load_custom_background, blend_background

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

    # 2. Apply theme or custom background
    if background:
        bg_img = load_custom_background(background, (width, height))
        img = blend_background(img, bg_img, opacity=0.7)
    elif theme:
        bg_img = load_theme_background(theme, preset, (width, height), seed=seed)
        img = blend_background(img, bg_img, opacity=0.8)

    # 3. Apply gradient overlay (subtle colored gradient from bottom)
    if effects_cfg.get("gradient_overlay", False):
        img = apply_gradient_overlay(
            img,
            color=preset["accent"],
            opacity=0.15,
            direction="bottom",
        )

    # 4. Apply vignette (darken edges)
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

    # Position based on layout style
    layout_style = layout_cfg.get("text_position", "center")
    if layout_style == "left":
        x = margin
        y = (height - text_height) // 2 - 20
    elif layout_style == "upper-center":
        x = (width - text_width) // 2
        y = height // 4 - text_height // 2
    else:  # center
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 40

    # 5. Draw text with effects (shadow → glow → main text)
    img = draw_title(img, text, font, (x, y), config, preset)

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")

    return output_path


def render_variations(
    title: str,
    preset_name: str = "focus",
    output_dir: str | Path = "output",
    config: dict | None = None,
    theme: str | None = None,
    background: str | None = None,
    count: int = 3,
) -> list[Path]:
    """Generate multiple thumbnail variations with different layouts and seeds.

    Each variation uses a different text position and random seed for the theme.
    """
    import copy

    if config is None:
        config = load_brand_config()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    layouts = ["center", "left", "upper-center"]
    paths = []

    for i in range(min(count, len(layouts))):
        # Create a config variant with different layout
        var_config = copy.deepcopy(config)
        var_config["layout"]["text_position"] = layouts[i]

        filename = f"thumb_{i + 1:02d}_{layouts[i]}.png"
        path = render_thumbnail(
            title=title,
            preset_name=preset_name,
            output_path=output_dir / filename,
            config=var_config,
            theme=theme,
            background=background,
            seed=i * 37 + 7,  # Different seed per variation
        )
        paths.append(path)

    return paths


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _load_font(family: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a font by family name, fall back to bundled fonts."""
    # Project fonts directory
    project_root = Path(__file__).parent.parent
    fonts_dir = project_root / "fonts"

    # Try exact family name in fonts/
    font_paths = [
        fonts_dir / f"{family}.ttf",
        fonts_dir / f"{family}.otf",
        Path(f"/System/Library/Fonts/{family}.ttf"),
        Path(f"/System/Library/Fonts/Supplemental/{family}.ttf"),
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(str(path), size)
        except (OSError, IOError):
            continue

    # Try system font by name
    try:
        return ImageFont.truetype(family, size)
    except (OSError, IOError):
        pass

    # Fall back to bundled Bebas Neue (our primary font)
    bebas = fonts_dir / "BebasNeue-Regular.ttf"
    if bebas.exists():
        return ImageFont.truetype(str(bebas), size)

    # Last resort: Pillow default
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()
