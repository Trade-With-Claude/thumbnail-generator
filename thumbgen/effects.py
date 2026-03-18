import math

from PIL import Image, ImageDraw

from thumbgen.renderer import _hex_to_rgb


def apply_vignette(img: Image.Image, strength: float = 0.6) -> Image.Image:
    """Apply a radial vignette effect — darken the edges of the image.

    Args:
        img: Input image
        strength: 0.0 (no effect) to 1.0 (full black edges)

    Returns:
        Image with vignette applied
    """
    width, height = img.size
    cx, cy = width // 2, height // 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)

    # Create a dark overlay with radial transparency
    vignette = Image.new("RGBA", img.size, (0, 0, 0, 0))

    # Build pixel by pixel would be slow — use a smaller version and resize
    small_w, small_h = width // 4, height // 4
    small_cx, small_cy = small_w // 2, small_h // 2
    small_max = math.sqrt(small_cx ** 2 + small_cy ** 2)

    small_vig = Image.new("RGBA", (small_w, small_h), (0, 0, 0, 0))
    pixels = small_vig.load()

    for y in range(small_h):
        for x in range(small_w):
            dx = x - small_cx
            dy = y - small_cy
            dist = math.sqrt(dx ** 2 + dy ** 2)
            # Normalize distance and apply curve
            norm = dist / small_max
            # Start darkening after 40% from center
            if norm > 0.4:
                alpha = int(((norm - 0.4) / 0.6) ** 1.5 * 255 * strength)
                alpha = min(alpha, 255)
                pixels[x, y] = (0, 0, 0, alpha)

    # Resize to full image size with smooth interpolation
    vignette = small_vig.resize(img.size, Image.LANCZOS)

    return Image.alpha_composite(img.convert("RGBA"), vignette).convert("RGB")


def apply_gradient_overlay(
    img: Image.Image,
    color: str = "#000000",
    opacity: float = 0.4,
    direction: str = "bottom",
) -> Image.Image:
    """Apply a gradient overlay from one edge of the image.

    Args:
        img: Input image
        color: Hex color for the gradient
        opacity: Max opacity of the gradient (0.0-1.0)
        direction: "bottom" (gradient from bottom up) or "top"

    Returns:
        Image with gradient applied
    """
    width, height = img.size
    rgb = _hex_to_rgb(color)

    gradient = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)

    # Draw horizontal lines with increasing opacity
    gradient_height = height // 2  # Gradient covers bottom half

    for y in range(gradient_height):
        if direction == "bottom":
            line_y = height - gradient_height + y
            progress = y / gradient_height
        else:
            line_y = gradient_height - 1 - y
            progress = y / gradient_height

        alpha = int(progress * 255 * opacity)
        draw.line([(0, line_y), (width, line_y)], fill=(*rgb, alpha))

    return Image.alpha_composite(img.convert("RGBA"), gradient).convert("RGB")
