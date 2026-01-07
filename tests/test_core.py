"""Tests for the core ImageProcessor class."""

import os
import tempfile

import pytest
from PIL import Image

from imgop.core import ImageProcessor


class TestImageProcessor:
    """Test cases for ImageProcessor class."""

    def test_scale_size(self):
        """Test the scale_size static method."""
        assert ImageProcessor.scale_size((100, 200), 2) == (50, 100)
        assert ImageProcessor.scale_size((1000, 500), 10) == (100, 50)

    def test_init_default_quality(self):
        """Test ImageProcessor initialization with default quality."""
        processor = ImageProcessor()
        assert processor.quality == 85

    def test_init_custom_quality(self):
        """Test ImageProcessor initialization with custom quality."""
        processor = ImageProcessor(quality=95)
        assert processor.quality == 95

    def test_make_resized_large_image(self):
        """Test resizing a large image."""
        processor = ImageProcessor()

        # Create a test image larger than 1000px
        img = Image.new("RGB", (2000, 1500), color="red")
        resized = processor.make_resized(img)

        # Should be reduced by factor of 2 (2000/1000 = 2)
        assert resized.size == (1000, 750)

    def test_make_resized_small_image(self):
        """Test resizing a small image."""
        processor = ImageProcessor()

        # Create a test image smaller than 1000px
        img = Image.new("RGB", (800, 600), color="blue")
        resized = processor.make_resized(img)

        # Should be reduced by factor of 2 (default)
        assert resized.size == (400, 300)

    def test_make_thumbnail(self):
        """Test thumbnail creation."""
        processor = ImageProcessor()

        # Create a test image
        img = Image.new("RGB", (1000, 800), color="green")
        thumbnail = processor.make_thumbnail(img)

        # Should be square
        assert thumbnail.size[0] == thumbnail.size[1]

    def test_process_nonexistent_path(self):
        """Test processing a nonexistent path."""
        processor = ImageProcessor()

        with pytest.raises(FileNotFoundError):
            processor.process_path("/nonexistent/path")

    def test_save_image(self):
        """Test saving an image."""
        processor = ImageProcessor()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="yellow")

            # Save the image (filename without extension)
            processor.save_image(img, "test", temp_dir)

            # Check if file was created
            output_path = os.path.join(temp_dir, "test.jpg")
            assert os.path.exists(output_path)

            # Verify it's a valid image
            saved_img = Image.open(output_path)
            assert saved_img.size == (100, 100)
