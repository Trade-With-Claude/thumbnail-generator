import click
from pathlib import Path

from thumbgen.config import load_brand_config
from thumbgen.renderer import render_thumbnail, render_variations


@click.command()
@click.option("--title", required=True, help="Title text for the thumbnail (3-5 words)")
@click.option("--subtitle", default=None, help="Optional subtitle text")
@click.option("--preset", default="focus", type=click.Choice(["focus", "sleep", "meditation"]), help="Color preset")
@click.option("--theme", default=None, type=click.Choice(["brain", "abstract"]), help="Background theme")
@click.option("--background", default=None, help="Path to custom background image")
@click.option("--seed", default=None, type=int, help="Random seed for reproducible generation")
@click.option("--variations", default=1, type=click.IntRange(1, 3), help="Number of variations to generate (1-3)")
@click.option("--output", default="output/", help="Output directory")
@click.option("--config", default=None, help="Path to brand.json (default: ./brand.json)")
def main(title: str, subtitle: str | None, preset: str, theme: str | None, background: str | None, seed: int | None, variations: int, output: str, config: str | None):
    """Generate YouTube thumbnails with brand-consistent styling."""
    brand_config = load_brand_config(config)

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if variations > 1:
        paths = render_variations(
            title=title,
            preset_name=preset,
            output_dir=output_dir,
            config=brand_config,
            theme=theme,
            background=background,
            count=variations,
        )
        for p in paths:
            click.echo(f"  {p}")
        click.echo(f"{len(paths)} variations saved to {output_dir}/")
    else:
        output_path = output_dir / "thumbnail.png"
        path = render_thumbnail(
            title=title,
            preset_name=preset,
            output_path=output_path,
            config=brand_config,
            theme=theme,
            background=background,
            seed=seed,
        )
        click.echo(f"Thumbnail saved: {path}")


if __name__ == "__main__":
    main()
