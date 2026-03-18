import click
from pathlib import Path

from thumbgen.config import load_brand_config
from thumbgen.renderer import render_thumbnail


@click.command()
@click.option("--title", required=True, help="Title text for the thumbnail (3-5 words)")
@click.option("--preset", default="focus", type=click.Choice(["focus", "sleep", "meditation"]), help="Color preset")
@click.option("--output", default="output/", help="Output directory")
@click.option("--config", default=None, help="Path to brand.json (default: ./brand.json)")
def main(title: str, preset: str, output: str, config: str | None):
    """Generate a YouTube thumbnail with brand-consistent styling."""
    brand_config = load_brand_config(config)

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "thumbnail.png"

    path = render_thumbnail(
        title=title,
        preset_name=preset,
        output_path=output_path,
        config=brand_config,
    )

    click.echo(f"Thumbnail saved: {path}")


if __name__ == "__main__":
    main()
