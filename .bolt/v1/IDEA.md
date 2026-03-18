# Thumbnail Generator

## The Idea
Brand-consistent YouTube thumbnail generator for an ADHD music / binaural beats channel. Define a brand identity once (fonts, colors, layout, effects) in a config file, then auto-generate thumbnails for every video that look professional and cohesive.

## The Problem
Creating thumbnails manually in Canva takes time and results in inconsistent branding. For an automated YouTube pipeline, thumbnails need to be generated programmatically with consistent brand identity while still looking unique per video.

## Key Features
- **Brand identity config** — `brand.json` defining font, color palette, layout template, logo placement, effects (glow, gradient overlay, text shadow)
- **Thumbnail rendering** — Pillow-based renderer that composites background + text + brand overlays into 1280x720 images
- **Background sources** — extract a frame from generated visuals, use a solid/gradient color, or provide a custom image
- **Text placement** — SEO-optimized title text with configurable positioning, font size auto-scaling, text effects
- **Variation generation** — generate 2-3 thumbnail options per video (different color accents, text positions) to preview/pick
- **CLI interface** — `python generate.py --title "ADHD Deep Focus" --background frame.png` outputs thumbnail(s)
- **Integration ready** — output consumed by the upload pipeline in the youtube-autopilot ecosystem

## Stack / Tech Preferences
- **Python** — main language
- **Pillow (PIL)** — image rendering and compositing
- **Click or argparse** — CLI interface
- No web UI needed (CLI-first, could add later)
- No paid dependencies

## Notes
- Part of the youtube-autopilot ecosystem (3rd of 3 sub-projects: SEO engine, video generator, thumbnail generator)
- Thumbnails must be 1280x720 (YouTube optimal)
- Channel niche: ADHD music, meditation, binaural beats — thumbnails should feel calm, dreamy, space-like
- Brand identity is designed once and reused across all future thumbnails
- The upload pipeline will call this as a module or CLI command
