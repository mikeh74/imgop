"""Command line interface for imagefixer."""

import sys

import click

from .core import ImageProcessor


def validate_aspect_ratio(ctx, param, value):
    """Validate aspect ratio format."""
    if value is None:
        return value

    if ":" not in value:
        raise click.BadParameter("must be in format width:height (e.g., 16:9)")

    try:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError
        float(parts[0])
        float(parts[1])
    except ValueError:
        raise click.BadParameter(
            "must be in format width:height with numeric values (e.g., 16:9)"
        ) from None

    return value


@click.command(
    name="imgop",
    help="Resize and crop images with flexible options",
    epilog="""
Examples:
  imgop image.jpg                              # Process single image (default mode)
  imgop /path/to/images/                       # Process directory
  imgop image.jpg -o /output/                  # Specify output directory
  imgop image.jpg --scale 50                   # Scale to 50% of original size
  imgop image.jpg --width 800                  # Resize to width 800px (auto height)
  imgop image.jpg --size 1920 1080             # Resize to specific width and height
  imgop image.jpg --crop-size 800 600          # Crop to 800x600 from center
  imgop image.jpg --crop-aspect 16:9           # Crop to 16:9 aspect ratio
  imgop image.jpg --format webp                # Convert to WebP format
  imgop image.jpg --bw                         # Convert to black and white
  imgop image.jpg --scale 150 --format png     # Scale to 150% and save as PNG
""",
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
    "-t",
    "--thumbnail-quality",
    type=click.IntRange(1, 100),
    default=70,
    show_default=True,
    help="JPEG quality for thumbnails",
)
@click.option(
    "--scale",
    type=float,
    default=None,
    help="Scale image by percentage (e.g., 50 for 50%, 150 for 150%)",
)
@click.option(
    "--width",
    type=int,
    default=None,
    help="Resize to specific width (height calculated automatically)",
)
@click.option(
    "--height",
    type=int,
    default=None,
    help="Resize to specific height (width calculated automatically)",
)
@click.option(
    "--size",
    type=(int, int),
    default=None,
    metavar="WIDTH HEIGHT",
    help="Resize to specific width and height",
)
@click.option(
    "--crop-size",
    type=(int, int),
    default=None,
    metavar="WIDTH HEIGHT",
    help="Crop to specific width and height from center",
)
@click.option(
    "--crop-aspect",
    type=str,
    default=None,
    callback=validate_aspect_ratio,
    help="Crop to specific aspect ratio (e.g., 16:9, 4:3, 1:1)",
)
@click.option(
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
@click.version_option(version="0.1.0", prog_name="imgop")
def main(
    path,
    output,
    quality,
    thumbnail_quality,
    scale,
    width,
    height,
    size,
    crop_size,
    crop_aspect,
    output_format,
    black_and_white,
):
    """Main entry point for the CLI."""
    try:
        # Validate scale
        if scale is not None and scale <= 0:
            raise click.BadParameter("Scale must be greater than 0", param_hint="scale")

        # Validate width
        if width is not None and width <= 0:
            raise click.BadParameter("Width must be greater than 0", param_hint="width")

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
                size is not None,
            ]
        )
        if resize_options > 1:
            raise click.UsageError(
                "Cannot use multiple resize options (scale, width, height, size) together"
            )

        # Check for conflicting crop options
        crop_options = sum([crop_size is not None, crop_aspect is not None])
        if crop_options > 1:
            raise click.UsageError(
                "Cannot use multiple crop options (crop-size, crop-aspect) together"
            )

        # Determine if using default mode (no special options)
        use_default_mode = all(
            [
                scale is None,
                width is None,
                height is None,
                size is None,
                crop_size is None,
                crop_aspect is None,
                output_format is None,
                not black_and_white,
            ]
        )

        processor = ImageProcessor(
            quality=quality,
            thumbnail_quality=thumbnail_quality,
            scale=scale,
            width=width,
            height=height,
            size=size,
            crop_size=crop_size,
            crop_aspect=crop_aspect,
            output_format=output_format,
            black_and_white=black_and_white,
            default_mode=use_default_mode,
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
