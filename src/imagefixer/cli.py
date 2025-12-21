"""Command line interface for imagefixer."""

import argparse
import sys

from .core import ImageProcessor


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="imagefixer",
        description="Resize and crop images with flexible options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  imagefixer image.jpg                              # Process single image (default mode)
  imagefixer /path/to/images/                       # Process directory
  imagefixer image.jpg -o /output/                  # Specify output directory
  imagefixer image.jpg --scale 50                   # Scale to 50% of original size
  imagefixer image.jpg --width 800                  # Resize to width 800px (auto height)
  imagefixer image.jpg --size 1920 1080             # Resize to specific width and height
  imagefixer image.jpg --crop-size 800 600          # Crop to 800x600 from center
  imagefixer image.jpg --crop-aspect 16:9           # Crop to 16:9 aspect ratio
  imagefixer image.jpg --format webp                # Convert to WebP format
  imagefixer image.jpg --scale 150 --format png     # Scale to 150% and save as PNG
        """.strip(),
    )

    parser.add_argument(
        "path", help="Path to image file or directory containing images"
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="Output directory (default: same as input)",
        default=None,
    )

    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        help="Output quality for JPEG/WebP (1-100, default: 85)",
    )

    parser.add_argument(
        "-t",
        "--thumbnail-quality",
        type=int,
        default=70,
        help="JPEG quality for thumbnails (1-100, default: 70)",
    )

    # Scaling options
    parser.add_argument(
        "--scale",
        type=float,
        help="Scale image by percentage (e.g., 50 for 50%%, 150 for 150%%)",
        default=None,
    )

    # Resize options
    parser.add_argument(
        "--width",
        type=int,
        help="Resize to specific width (height calculated automatically)",
        default=None,
    )

    parser.add_argument(
        "--height",
        type=int,
        help="Resize to specific height (width calculated automatically)",
        default=None,
    )

    parser.add_argument(
        "--size",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        help="Resize to specific width and height",
        default=None,
    )

    # Crop options
    parser.add_argument(
        "--crop-size",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        help="Crop to specific width and height from center",
        default=None,
    )

    parser.add_argument(
        "--crop-aspect",
        type=str,
        help="Crop to specific aspect ratio (e.g., 16:9, 4:3, 1:1)",
        default=None,
    )

    # Format options
    parser.add_argument(
        "--format",
        type=str,
        choices=["jpeg", "jpg", "png", "webp"],
        help="Output format (jpeg, png, or webp)",
        default=None,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if not 1 <= args.quality <= 100:
        raise ValueError("Quality must be between 1 and 100")

    if not 1 <= args.thumbnail_quality <= 100:
        raise ValueError("Thumbnail quality must be between 1 and 100")

    if args.scale is not None and args.scale <= 0:
        raise ValueError("Scale must be greater than 0")

    if args.width is not None and args.width <= 0:
        raise ValueError("Width must be greater than 0")

    if args.height is not None and args.height <= 0:
        raise ValueError("Height must be greater than 0")

    # Check for conflicting resize options
    resize_options = sum(
        [
            args.scale is not None,
            args.width is not None,
            args.height is not None,
            args.size is not None,
        ]
    )
    if resize_options > 1:
        raise ValueError(
            "Cannot use multiple resize options "
            "(scale, width, height, size) together"
        )

    # Check for conflicting crop options
    crop_options = sum([args.crop_size is not None, args.crop_aspect is not None])
    if crop_options > 1:
        raise ValueError(
            "Cannot use multiple crop options " "(crop-size, crop-aspect) together"
        )

    # Validate aspect ratio format
    if args.crop_aspect:
        if ":" not in args.crop_aspect:
            raise ValueError("Aspect ratio must be in format width:height (e.g., 16:9)")
        try:
            parts = args.crop_aspect.split(":")
            if len(parts) != 2:
                raise ValueError
            float(parts[0])
            float(parts[1])
        except ValueError:
            raise ValueError(
                "Aspect ratio must be in format width:height "
                "with numeric values (e.g., 16:9)"
            ) from None


def main(argv: list | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        validate_args(args)

        # Determine if using default mode (no special options)
        use_default_mode = all(
            [
                args.scale is None,
                args.width is None,
                args.height is None,
                args.size is None,
                args.crop_size is None,
                args.crop_aspect is None,
                args.format is None,
            ]
        )

        processor = ImageProcessor(
            quality=args.quality,
            thumbnail_quality=args.thumbnail_quality,
            scale=args.scale,
            width=args.width,
            height=args.height,
            size=args.size,
            crop_size=args.crop_size,
            crop_aspect=args.crop_aspect,
            output_format=args.format,
            default_mode=use_default_mode,
        )

        processor.process_path(args.path, args.output)

        print(f"✅ Successfully processed: {args.path}")
        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
