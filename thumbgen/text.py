from PIL import Image, ImageDraw, ImageFilter, ImageFont

from thumbgen.renderer import _hex_to_rgb


def draw_title(
    img: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    position: tuple[int, int],
    config: dict,
    preset: dict,
) -> Image.Image:
    """Draw title text with drop shadow and outer glow effects.

    Effects are applied in order: shadow → glow → main text.
    Returns the modified image.
    """
    effects_cfg = config.get("effects", {})

    # Drop shadow
    if effects_cfg.get("text_shadow", False):
        shadow_offset = effects_cfg.get("text_shadow_offset", [4, 4])
        shadow_color = _hex_to_rgb(effects_cfg.get("text_shadow_color", "#000000"))
        shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])

        shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text(shadow_pos, text, font=font, fill=(*shadow_color, 180))

        # Blur the shadow slightly for softness
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=3))
        img = Image.alpha_composite(img.convert("RGBA"), shadow_layer).convert("RGB")

    # Outer glow
    if effects_cfg.get("text_glow", False):
        glow_color = _hex_to_rgb(preset.get("text_glow_color", "#FFFFFF"))
        glow_radius = effects_cfg.get("text_glow_radius", 8)

        glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.text(position, text, font=font, fill=(*glow_color, 120))

        # Multiple blur passes for a smooth glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius // 2))

        img = Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB")

    # Main text
    text_color = _hex_to_rgb(config["font"].get("color", "#FFFFFF"))
    draw = ImageDraw.Draw(img)
    draw.text(position, text, font=font, fill=text_color)

    return img
