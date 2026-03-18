import json
from pathlib import Path

# Default brand.json location
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "brand.json"

REQUIRED_KEYS = ["font", "canvas", "presets", "layout", "effects"]
REQUIRED_PRESET_KEYS = ["accent", "accent_secondary", "background_tint", "text_glow_color"]


def load_brand_config(config_path: Path | str | None = None) -> dict:
    """Load and validate brand.json configuration."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        raise FileNotFoundError(f"Brand config not found: {path}")

    with open(path) as f:
        config = json.load(f)

    # Validate top-level keys
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Missing required key in brand.json: {key}")

    # Validate presets
    presets = config.get("presets", {})
    if not presets:
        raise ValueError("brand.json must have at least one preset in 'presets'")

    for preset_name, preset_data in presets.items():
        for key in REQUIRED_PRESET_KEYS:
            if key not in preset_data:
                raise ValueError(f"Preset '{preset_name}' missing required key: {key}")

    return config


def get_preset(config: dict, preset_name: str) -> dict:
    """Get a specific color preset from the config."""
    presets = config.get("presets", {})
    if preset_name not in presets:
        available = ", ".join(presets.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    return presets[preset_name]
