"""Command line interface for imgop."""

import sys

import click

from imgop.core import ImageProcessor


def validate_crop_option(ctx, param, value):
    """Validate crop option - accepts percentage value only."""
    if not value:
        return None

    try:
        percent = float(value)
        if percent <= 0 or percent >= 100:
            raise click.BadParameter(
                "Crop percentage must be between 0 and 100",
            )
        return percent
    except ValueError:
        raise click.BadParameter(
            "Must be a numeric percentage value (e.g., 50 for 50%)"
        ) from None


@click.command(
    name="imgop",
    help="Resize and crop images with flexible options",
)
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output directory (default: same as input)",
)
@click.option(
    "-q",
    "--quality",
    type=click.IntRange(1, 100),
    default=85,
    show_default=True,
    help="Output quality for JPEG/WebP",
)
@click.option(
    "--scale",
    type=float,
    default=None,
    help="Scale image by percentage (e.g., 50 for 50%, 150 for 150%)",
)
@click.option(
    "-w",
    "--width",
    type=int,
    default=None,
    help="Resize to specific width (height calculated automatically)",
)
@click.option(
    "-h",
    "--height",
    type=int,
    default=None,
    help="Resize to specific height (width calculated automatically)",
)
@click.option(
    "-c",
    "--crop",
    type=int,
    default=None,
    metavar="PERCENT",
    callback=validate_crop_option,
    help="Crop to percentage of original size (e.g., -c 50 for 50%)",
)
@click.option(
    "-a",
    "--aspect-ratio",
    type=click.Choice(
        ["16:9", "5:3", "4:3", "3:4", "3:2", "1:1"],
        case_sensitive=False,
    ),
    default=None,
    help="Crop to specific aspect ratio",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["jpeg", "jpg", "png", "webp"], case_sensitive=False),
    default=None,
    help="Output format (jpeg, png, or webp)",
)
@click.option(
    "--bw",
    "--black-and-white",
    "black_and_white",
    is_flag=True,
    default=False,
    help="Convert image to black and white (grayscale)",
)
@click.option(
    "-t",
    "--thumb",
    "--thumbnail",
    "thumbnail",
    is_flag=True,
    default=False,
    help="Create square thumbnail (saved with _sm suffix)",
)
@click.version_option(version="0.7.0", prog_name="imgop")
def main(
    path,
    output,
    quality,
    scale,
    width,
    height,
    crop,
    aspect_ratio,
    output_format,
    black_and_white,
    thumbnail,
):
    """Main entry point for the CLI."""
    try:
        # Validate scale
        if scale is not None and scale <= 0:
            raise click.BadParameter(
                "Scale must be greater than 0",
                param_hint="scale",
            )

        # Validate width
        if width is not None and width <= 0:
            raise click.BadParameter(
                "Width must be greater than 0",
                param_hint="width",
            )

        # Validate height
        if height is not None and height <= 0:
            raise click.BadParameter(
                "Height must be greater than 0", param_hint="height"
            )

        # Check for conflicting resize options
        resize_options = sum(
            [
                scale is not None,
                width is not None,
                height is not None,
            ]
        )
        if resize_options > 1:
            raise click.UsageError(
                "Cannot use multiple resize options (scale, width, height) together"
            )

        # Crop option returns percentage value directly
        crop_percent = crop
        # Check if thumbnail conflicts with transformation options
        if thumbnail and (
            scale is not None
            or width is not None
            or height is not None
            or crop_percent is not None
            or aspect_ratio is not None
        ):
            raise click.UsageError(
                "Cannot use --thumb with other resize or crop options"
            )

        # Determine if using default mode (no special options)
        use_default_mode = all(
            [
                scale is None,
                width is None,
                height is None,
                crop_percent is None,
                aspect_ratio is None,
                output_format is None,
                not black_and_white,
                not thumbnail,
            ]
        )

        # Configure processor based on mode
        if use_default_mode:
            # Default mode: scale by 50% with _md suffix
            processor = ImageProcessor(
                quality=quality,
                scale=50,
                suffix="_md",
            )
        elif thumbnail:
            # Thumbnail mode: crop to 1:1 aspect and scale by 25% with _sm suffix
            processor = ImageProcessor(
                quality=quality,
                scale=25,
                crop_aspect="1:1",
                suffix="_sm",
            )
        else:
            # Custom mode: use specified parameters
            processor = ImageProcessor(
                quality=quality,
                scale=scale,
                width=width,
                height=height,
                crop_aspect=aspect_ratio,
                crop_percent=crop_percent,
                output_format=output_format,
                black_and_white=black_and_white,
            )

        processor.process_path(path, output)

        click.echo(f"✅ Successfully processed: {path}")

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except (click.BadParameter, click.UsageError):
        raise
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
