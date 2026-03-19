# Roadmap — V1

## Phase 1: Foundation
**Goal:** Project skeleton — config system, brand.json, Pillow setup, basic rendering
**Requirements:**
- R1: Python project structure with `thumbgen/` package, requirements.txt (Pillow, Click)
- R2: `brand.json` config with font, colors (focus/sleep/meditation presets), layout, effects
- R3: Config loader that reads and validates brand.json
- R4: Basic renderer that creates a 1280x720 dark canvas and saves as PNG
**Success:** `python generate.py --title "TEST"` outputs a 1280x720 PNG with text on a dark background

## Phase 2: Text & Effects
**Goal:** Bold text rendering with auto-sizing, glow, shadow, and vignette effects
**Requirements:**
- R1: Text auto-sizing — fits 3-5 words within safe zone, bold caps, readable at small size
- R2: Text effects — outer glow, drop shadow, configurable from brand.json
- R3: Background effects — vignette, gradient overlay, darkened edges
- R4: Color presets — apply focus/sleep/meditation palettes from brand.json
**Success:** Generated thumbnail has bold glowing text with vignette, using the correct color preset

## Phase 3: Themes & Backgrounds
**Goal:** Two themes (Brain/Neural + Abstract/Cosmic) with background compositing
**Requirements:**
- R1: Theme asset system — load images from `themes/brain/` and `themes/abstract/`
- R2: Background compositing — overlay/blend theme assets with dark base + color tinting
- R3: Custom background support — accept a frame image from video-generator as input
- R4: Theme selection via CLI (`--theme brain` or `--theme abstract`)
**Success:** `python generate.py --title "ADHD FOCUS" --theme brain --preset focus` produces a thumbnail with brain imagery background

## Phase 4: Variations & CLI
**Goal:** Generate 2-3 variations per run with full CLI interface
**Requirements:**
- R1: Variation engine — generate 2-3 options with different layouts (centered, left-aligned, split), color shifts, and background crops
- R2: Full CLI — `--title`, `--subtitle`, `--theme`, `--preset`, `--background`, `--variations`, `--output`
- R3: Output naming — `output/thumb_001_centered.png`, `thumb_001_left.png`, etc.
- R4: Bundled fonts — ship Montserrat Bold or Bebas Neue in the project
**Success:** Single CLI command generates 3 distinct thumbnail variations in the output folder, all brand-consistent
