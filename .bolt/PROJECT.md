# Thumbnail Generator

## Project Name
Thumbnail Generator

## Description
CLI-based YouTube thumbnail generator with brand consistency for an ADHD music / binaural beats channel. Generates 1280x720 thumbnails from templates with configurable brand identity, text overlays, and effects. Outputs ready-to-upload images consumed by the youtube-autopilot upload pipeline.

## Repository
thumbnail-generator

## Users
- Primary: channel owner (ADHD music / binaural beats, ~1,200 subs)
- Usage: CLI command as part of the youtube-autopilot pipeline
- Single user, automation-focused

## UX
- CLI-first: `python generate.py --title "ADHD FOCUS" --theme brain --preset focus`
- No web UI (v1)
- Outputs 2-3 thumbnail variations to an output folder for quick preview/pick
- Integration: called by upload pipeline or manually

## Architecture
- **Language:** Python
- **Rendering:** Pillow (PIL) for image compositing
- **CLI:** Click or argparse
- **Config:** `brand.json` for brand identity + `themes/` folder for theme assets
- **No external APIs** — purely local image generation
- **No paid dependencies**

## Brand Identity

### Font
- Bold sans-serif, all caps (Montserrat Bold, Bebas Neue, or similar)
- Primary text: 3-5 words max, must be readable at 160x90px (mobile)
- Optional subtitle in lighter weight, smaller size

### Colors (by content type)
- **Focus/ADHD:** Teal/cyan + amber/gold accents on dark background
- **Sleep/Relaxation:** Deep blue + purple, minimal warm accents
- **Meditation/Healing:** Purple + white/golden light accents
- All types: dark base (#0a0a0a to #1a1a2e), luminous glowing accents

### Layout
- Text position: upper-center or left-aligned
- Avoid bottom-right (YouTube duration stamp)
- 2-3 template layouts that rotate: centered, left-aligned, split
- No logo/watermark

### Effects
- Glow/bloom on text (outer glow, subtle)
- Gradient overlay on background (darken edges, vignette)
- Text shadow for readability
- Luminous accent particles/light streaks

### Themes (2 themes)
1. **Brain/Neural** — brain imagery, neural network patterns, synaptic visuals. Best for ADHD-specific content.
2. **Abstract/Cosmic** — particles, gradients, aurora, fractals. Best for meditation, ambient, general relaxation.

### What Changes Per Video
- Title text
- Color accent (within the content-type palette)
- Background image (frame from video generator or theme asset)
- Theme choice (brain vs abstract)

### What Stays Fixed
- Font family and weight
- Text position/layout
- Glow/effect style
- Overall dark + luminous aesthetic

## Project Structure
```
thumbnail-generator/
├── generate.py           # CLI entry point
├── brand.json            # Brand identity config
├── thumbgen/
│   ├── __init__.py
│   ├── renderer.py       # Core rendering engine (Pillow)
│   ├── text.py           # Text placement, auto-sizing, effects
│   ├── effects.py        # Glow, gradient overlay, vignette
│   ├── themes.py         # Theme loading and application
│   └── config.py         # Brand config loading
├── themes/
│   ├── brain/            # Brain/neural theme assets
│   └── abstract/         # Abstract/cosmic theme assets
├── output/               # Generated thumbnails land here
├── requirements.txt
└── tests/
```

## Technical Constraints
- Output: 1280x720 PNG (YouTube optimal)
- Must pass "squint test" — readable at 160x90px
- Pillow only — no ImageMagick dependency
- Font files bundled in project (no system font dependency)
- Should generate 2-3 variations per run

## Ecosystem
- 3rd of 3 sub-projects in youtube-autopilot (SEO engine, video generator, thumbnail generator)
- Thumbnail output consumed by upload pipeline
- Can use frames from video-generator as background input
- Title text can come from SEO engine metadata
