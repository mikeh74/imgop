"""Core image processing functionality."""

import os
from pathlib import Path

from PIL import Image


class ImageProcessor:
    """Main class for image processing operations."""

    def __init__(
        self,
        quality: int = 85,
        thumbnail_quality: int = 70,
        scale: float | None = None,
        width: int | None = None,
        height: int | None = None,
        size: tuple[int, int] | None = None,
        crop_size: tuple[int, int] | None = None,
        crop_aspect: str | None = None,
        crop_percent: float | None = None,
        output_format: str | None = None,
        black_and_white: bool = False,
        default_mode: bool = True,
        thumbnail_mode: bool = False,
    ):
        """Initialize ImageProcessor with quality and transformation settings.

        Args:
            quality: JPEG/WebP quality for resized images (1-100)
            thumbnail_quality: JPEG quality for thumbnails (1-100)
            scale: Scale percentage (e.g., 50 for 50%, 150 for 150%)
            width: Target width for resize (height auto-calculated)
            height: Target height for resize (width auto-calculated)
            size: Target (width, height) for resize
            crop_size: Crop to (width, height) from center
            crop_aspect: Crop to aspect ratio (e.g., "16:9")
            crop_percent: Crop to percentage of original size (e.g., 50 for 50%)
            output_format: Output format (jpeg, png, webp)
            black_and_white: Convert image to grayscale
            default_mode: Whether to use default thumbnail/resize behavior
            thumbnail_mode: Whether to create square thumbnail with _sm suffix
        """
        self.quality = quality
        self.thumbnail_quality = thumbnail_quality
        self.scale = scale
        self.width = width
        self.height = height
        self.size = tuple(size) if size else None
        self.crop_size = tuple(crop_size) if crop_size else None
        self.crop_aspect = crop_aspect
        self.crop_percent = crop_percent
        self.output_format = output_format
        self.black_and_white = black_and_white
        self.default_mode = default_mode
        self.thumbnail_mode = thumbnail_mode

    @staticmethod
    def scale_size(size: tuple[int, int], factor: int) -> tuple[int, int]:
        """Scale a size tuple by a factor.

        Args:
            size: (width, height) tuple
            factor: scaling factor

        Returns:
            Scaled (width, height) tuple
        """
        return (size[0] // factor, size[1] // factor)

    @staticmethod
    def correct_image_orientation(img: Image.Image) -> Image.Image:
        """Correct image orientation based on EXIF data.

        Args:
            img: PIL Image object

        Returns:
            Image with corrected orientation
        """
        try:
            # Get EXIF data
            exif = img.getexif()
            if exif is None:
                return img

            # EXIF orientation tag is 274 (0x0112)
            orientation = exif.get(274)

            if orientation is None:
                return img

            # Apply the appropriate transformation
            if orientation == 2:
                # Mirrored horizontally
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                # Rotated 180 degrees
                img = img.rotate(180, expand=True)
            elif orientation == 4:
                # Mirrored vertically
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                # Mirrored horizontally and rotated 90 degrees CCW
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img = img.rotate(90, expand=True)
            elif orientation == 6:
                # Rotated 90 degrees CCW
                img = img.rotate(270, expand=True)
            elif orientation == 7:
                # Mirrored horizontally and rotated 90 degrees CW
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                # Rotated 90 degrees CW
                img = img.rotate(90, expand=True)

        except (AttributeError, KeyError, TypeError):
            # If there's any issue reading EXIF, just return the original image
            pass

        return img

    def save_image(
        self,
        img: Image.Image,
        filename: str,
        outfile: str,
        quality: int | None = None,
        output_format: str | None = None,
    ) -> None:
        """Save image to specified location.

        Args:
            img: PIL Image object
            filename: output filename (without extension)
            outfile: output directory
            quality: quality override
            output_format: format override (jpeg, png, webp)
        """
        if quality is None:
            quality = self.quality

        if output_format is None:
            output_format = self.output_format

        # Determine file extension - always add proper extension
        if output_format:
            ext = "jpg" if output_format == "jpeg" else output_format
        else:
            # Default to jpg if no format specified
            ext = "jpg"

        full_filename = f"{filename}.{ext}"
        path = os.path.join(outfile, full_filename)

        # Convert RGBA to RGB for JPEG
        if output_format in ["jpeg", "jpg", None] and img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            mask = img.split()[3] if len(img.split()) == 4 else None
            rgb_img.paste(img, mask=mask)
            img = rgb_img

        # Save with appropriate parameters
        if output_format == "png":
            img.save(path, format="PNG", optimize=True)
        elif output_format == "webp":
            img.save(path, format="WEBP", quality=quality)
        else:
            img.save(path, format="JPEG", quality=quality)

    def make_resized(self, img: Image.Image) -> Image.Image:
        """Create a resized version of the image.

        Args:
            img: PIL Image object

        Returns:
            Resized PIL Image object
        """
        size = img.size
        factor = 2

        if size[0] > 1000:
            factor = size[0] // 1000

        new_size = self.scale_size(size, factor)
        return img.resize(new_size)

    def make_thumbnail(self, img: Image.Image) -> Image.Image:
        """Create a square thumbnail from the image.

        Args:
            img: PIL Image object

        Returns:
            Square thumbnail PIL Image object
        """
        factor = 2
        if img.size[0] > 1000:
            factor = img.size[0] // 1000

        # Reduce size by factor * 2
        size = self.scale_size(img.size, factor * 2)
        resized_img = img.resize(size)

        # Create square crop from center
        start_x = (size[0] - size[1]) // 2
        box = (start_x, 0, start_x + size[1], size[1])
        return resized_img.crop(box)

    def apply_scale(self, img: Image.Image, scale: float) -> Image.Image:
        """Scale image by percentage.

        Args:
            img: PIL Image object
            scale: Scale percentage (e.g., 50 for 50%, 150 for 150%)

        Returns:
            Scaled PIL Image object
        """
        factor = scale / 100.0
        new_width = int(img.size[0] * factor)
        new_height = int(img.size[1] * factor)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def resize_by_width(self, img: Image.Image, width: int) -> Image.Image:
        """Resize image to specific width, maintaining aspect ratio.

        Args:
            img: PIL Image object
            width: Target width

        Returns:
            Resized PIL Image object
        """
        aspect_ratio = img.size[1] / img.size[0]
        new_height = int(width * aspect_ratio)
        return img.resize((width, new_height), Image.Resampling.LANCZOS)

    def resize_by_height(self, img: Image.Image, height: int) -> Image.Image:
        """Resize image to specific height, maintaining aspect ratio.

        Args:
            img: PIL Image object
            height: Target height

        Returns:
            Resized PIL Image object
        """
        aspect_ratio = img.size[0] / img.size[1]
        new_width = int(height * aspect_ratio)
        return img.resize((new_width, height), Image.Resampling.LANCZOS)

    def resize_to_size(self, img: Image.Image, size: tuple[int, int]) -> Image.Image:
        """Resize image to specific width and height.

        Args:
            img: PIL Image object
            size: (width, height) tuple

        Returns:
            Resized PIL Image object
        """
        return img.resize(size, Image.Resampling.LANCZOS)

    def crop_to_size(self, img: Image.Image, size: tuple[int, int]) -> Image.Image:
        """Crop image to specific size from center.

        Args:
            img: PIL Image object
            size: (width, height) tuple to crop to

        Returns:
            Cropped PIL Image object
        """
        width, height = size
        img_width, img_height = img.size

        # Calculate crop box centered in image
        left = max(0, (img_width - width) // 2)
        top = max(0, (img_height - height) // 2)
        right = min(img_width, left + width)
        bottom = min(img_height, top + height)

        return img.crop((left, top, right, bottom))

    def crop_to_aspect(self, img: Image.Image, aspect_str: str) -> Image.Image:
        """Crop image to specific aspect ratio from center.

        Args:
            img: PIL Image object
            aspect_str: Aspect ratio as string (e.g., "16:9", "4:3")

        Returns:
            Cropped PIL Image object
        """
        # Parse aspect ratio
        parts = aspect_str.split(":")
        aspect_width = float(parts[0])
        aspect_height = float(parts[1])
        target_aspect = aspect_width / aspect_height

        img_width, img_height = img.size
        img_aspect = img_width / img_height

        if img_aspect > target_aspect:
            # Image is wider than target - crop width
            new_width = int(img_height * target_aspect)
            left = (img_width - new_width) // 2
            return img.crop((left, 0, left + new_width, img_height))
        else:
            # Image is taller than target - crop height
            new_height = int(img_width / target_aspect)
            top = (img_height - new_height) // 2
            return img.crop((0, top, img_width, top + new_height))

    def crop_by_percent(self, img: Image.Image, percent: float) -> Image.Image:
        """Crop image to percentage of original size from center.

        Args:
            img: PIL Image object
            percent: Percentage to crop to (e.g., 50 for 50%)

        Returns:
            Cropped PIL Image object
        """
        img_width, img_height = img.size
        factor = percent / 100.0

        # Calculate new dimensions
        new_width = int(img_width * factor)
        new_height = int(img_height * factor)

        # Calculate crop box centered in image
        left = (img_width - new_width) // 2
        top = (img_height - new_height) // 2
        right = left + new_width
        bottom = top + new_height

        return img.crop((left, top, right, bottom))

    def generate_suffix(self) -> str:
        """Generate a descriptive suffix based on applied operations.

        Returns:
            Suffix string describing the operations (e.g., "_scale_50" or "_w800")
        """
        parts = []

        # Add crop suffix
        if self.crop_size:
            parts.append(f"crop_{self.crop_size[0]}x{self.crop_size[1]}")
        elif self.crop_aspect:
            aspect_clean = self.crop_aspect.replace(":", "_")
            parts.append(f"aspect_{aspect_clean}")
        elif self.crop_percent:
            # Format percent without decimal if it's a whole number
            percent_str = (
                f"{self.crop_percent:.0f}"
                if self.crop_percent == int(self.crop_percent)
                else f"{self.crop_percent:.1f}".rstrip("0").rstrip(".")
            )
            parts.append(f"crop_{percent_str}pct")

        # Add resize suffix
        if self.scale:
            # Format scale without decimal if it's a whole number
            scale_str = (
                f"{self.scale:.0f}"
                if self.scale == int(self.scale)
                else f"{self.scale:.1f}".rstrip("0").rstrip(".")
            )
            parts.append(f"scale_{scale_str}")
        elif self.width:
            parts.append(f"w{self.width}")
        elif self.height:
            parts.append(f"h{self.height}")
        elif self.size:
            parts.append(f"{self.size[0]}x{self.size[1]}")

        # Add color effect suffix
        if self.black_and_white:
            parts.append("bw")

        return "_" + "_".join(parts) if parts else ""

    def apply_transformations(self, img: Image.Image) -> Image.Image:
        """Apply all configured transformations to an image.

        Args:
            img: PIL Image object

        Returns:
            Transformed PIL Image object
        """
        # Apply aspect ratio crop first if specified
        if self.crop_aspect:
            img = self.crop_to_aspect(img, self.crop_aspect)

        # Then apply percentage crop (after aspect ratio)
        if self.crop_percent:
            img = self.crop_by_percent(img, self.crop_percent)

        # Apply other crop operations
        if self.crop_size:
            img = self.crop_to_size(img, self.crop_size)

        # Apply resize operations
        if self.scale:
            img = self.apply_scale(img, self.scale)
        elif self.width:
            img = self.resize_by_width(img, self.width)
        elif self.height:
            img = self.resize_by_height(img, self.height)
        elif self.size:
            img = self.resize_to_size(img, self.size)

        # Apply color effects
        if self.black_and_white:
            img = img.convert("L")

        return img

    def process_image(self, imgfile: str, outfile: str) -> None:
        """Process a single image file.

        Args:
            imgfile: path to input image
            outfile: path to output directory
        """
        # Read the image
        img = Image.open(imgfile)

        # Correct orientation based on EXIF data (fixes HEIC rotation issues)
        img = self.correct_image_orientation(img)

        # Extract filename without extension
        pieces = os.path.split(imgfile)
        filename = os.path.splitext(pieces[1])[0]

        if self.default_mode:
            # Default mode: create resized version only
            self.save_image(self.make_resized(img), f"{filename}_md", outfile)
        elif self.thumbnail_mode:
            # Thumbnail mode: create square thumbnail
            self.save_image(
                self.make_thumbnail(img),
                f"{filename}_sm",
                outfile,
                self.thumbnail_quality,
            )
        else:
            # Custom mode: apply specified transformations
            transformed_img = self.apply_transformations(img)
            suffix = self.generate_suffix()
            output_filename = f"{filename}{suffix}"
            self.save_image(transformed_img, output_filename, outfile)

    def process_directory(self, directory: str, outfile: str) -> None:
        """Process all supported image files in a directory.

        Args:
            directory: path to input directory
            outfile: path to output directory
        """
        supported_extensions = [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in supported_extensions:
                    self.process_image(file_path, outfile)

    def process_path(self, input_path: str, output_path: str | None = None) -> None:
        """Process a file or directory of images.

        Args:
            input_path: path to input file or directory
            output_path: path to output directory (optional)

        Raises:
            FileNotFoundError: if input_path doesn't exist
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Path doesn't exist: {input_path}")

        # Determine output path if not provided
        if not output_path or not os.path.isdir(output_path):
            if os.path.isfile(input_path):
                output_path = os.path.split(input_path)[0]
            elif os.path.isdir(input_path):
                output_path = input_path

        # Ensure output directory exists
        Path(output_path).mkdir(parents=True, exist_ok=True)

        # Process based on input type
        if os.path.isfile(input_path):
            self.process_image(input_path, output_path)
        elif os.path.isdir(input_path):
            self.process_directory(input_path, output_path)
