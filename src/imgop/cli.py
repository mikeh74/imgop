"""Command line interface for imgop."""

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


def validate_crop_option(ctx, param, value):
    """Validate crop option - accepts either 'WIDTH HEIGHT' or 'ASPECT_RATIO'."""
    if not value:
        return None, None

    value = value.strip()

    # Check if it's an aspect ratio (contains colon)
    if ":" in value:
        try:
            parts = value.split(":")
            if len(parts) != 2:
                raise ValueError
            float(parts[0])
            float(parts[1])
            return None, value
        except ValueError:
            raise click.BadParameter(
                "Aspect ratio must be in format width:height with numeric values (e.g., 5:4, 16:9)"
            ) from None

    # Check if it's dimensions (space-separated width and height)
    parts = value.split()
    if len(parts) == 2:
        try:
            width = int(parts[0])
            height = int(parts[1])
            if width <= 0 or height <= 0:
                raise click.BadParameter("Crop dimensions must be greater than 0")
            return (width, height), None
        except ValueError:
            raise click.BadParameter(
                "Dimensions must be two integers (e.g., '500 400')"
            ) from None

    raise click.BadParameter(
        "Must be either 'WIDTH HEIGHT' (e.g., '500 400') or 'ASPECT_RATIO' (e.g., '16:9')"
    )


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
    "--size",
    type=(int, int),
    default=None,
    metavar="WIDTH HEIGHT",
    help="Resize to specific width and height",
)
@click.option(
    "-c",
    "--crop",
    type=str,
    default=None,
    metavar="VALUE",
    callback=validate_crop_option,
    help="Crop to dimensions (e.g., -c '500 400') or aspect ratio (e.g., -c 16:9)",
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
@click.version_option(version="0.6.6", prog_name="imgop")
def main(
    path,
    output,
    quality,
    thumbnail_quality,
    scale,
    width,
    height,
    size,
    crop,
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
                size is not None,
            ]
        )
        if resize_options > 1:
            raise click.UsageError(
                "Cannot use multiple resize options (scale, width, height, size) together"
            )

        # Unpack crop option (returns tuple of crop_size and crop_aspect)
        crop_size, crop_aspect = crop if crop else (None, None)
        # Check if thumbnail conflicts with transformation options
        if thumbnail and (
            scale is not None
            or width is not None
            or height is not None
            or size is not None
            or crop_size is not None
            or crop_aspect is not None
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
                size is None,
                crop_size is None,
                crop_aspect is None,
                output_format is None,
                not black_and_white,
                not thumbnail,
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
            thumbnail_mode=thumbnail,
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
