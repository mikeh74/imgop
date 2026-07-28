"""Tests for the CLI module."""

import os
import tempfile

from click.testing import CliRunner
from PIL import Image

from imgop.cli import main


class TestCLI:
    """Test cases for CLI functionality."""

    def test_main_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "imgop" in result.output
        assert "Resize and crop images" in result.output

    def test_main_version(self):
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.7.2" in result.output

    def test_main_file_not_found(self):
        """Test main function with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.jpg"])
        assert result.exit_code == 2  # Click returns 2 for invalid path
        assert "does not exist" in result.output

    def test_conflicting_resize_options(self):
        """Test that conflicting resize options are rejected."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            result = runner.invoke(main, [tmp_path, "--scale", "50", "--width", "800"])
            assert result.exit_code != 0
            assert "Cannot use multiple resize options" in result.output
        finally:
            os.unlink(tmp_path)

    def test_thumbnail_with_resize_conflict(self):
        """Test that thumbnail with other resize options is rejected."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            result = runner.invoke(main, [tmp_path, "--thumb", "--scale", "50"])
            assert result.exit_code != 0
            assert (
                "Cannot use --thumb with other resize or crop options" in result.output
            )
        finally:
            os.unlink(tmp_path)

    def test_default_mode_creates_md_suffix(self):
        """Test that default mode creates files with _md suffix."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test image
            test_img_path = os.path.join(temp_dir, "test.jpg")
            img = Image.new("RGB", (200, 200), color="blue")
            img.save(test_img_path)

            # Run with default mode (no options)
            result = runner.invoke(main, [test_img_path, "-o", temp_dir])
            assert result.exit_code == 0
            assert "Successfully processed" in result.output

            # Check that output file exists with _lg suffix
            output_path = os.path.join(temp_dir, "test_lg.jpg")
            assert os.path.exists(output_path), f"Expected {output_path} to exist"

            # Verify it's a valid image
            output_img = Image.open(output_path)
            assert output_img.size == (1200, 1200)

    def test_thumbnail_mode_creates_sm_suffix(self):
        """Test that thumbnail mode creates files with _sm suffix."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test image
            test_img_path = os.path.join(temp_dir, "test.jpg")
            img = Image.new("RGB", (200, 200), color="green")
            img.save(test_img_path)

            # Run with thumbnail mode
            result = runner.invoke(main, [test_img_path, "-o", temp_dir, "--thumb"])
            assert result.exit_code == 0
            assert "Successfully processed" in result.output

            # Check that output file exists with _sm suffix
            output_path = os.path.join(temp_dir, "test_sm.jpg")
            assert os.path.exists(output_path), f"Expected {output_path} to exist"

            # Verify it's a valid image and square
            output_img = Image.open(output_path)
            assert output_img.size == (250, 250)
            assert output_img.size[0] == output_img.size[1]  # Square

    def test_format_option_accepts_heic(self):
        """Test that the CLI accepts HEIC as an output format."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_img_path = os.path.join(temp_dir, "test.jpg")
            img = Image.new("RGB", (100, 100), color="purple")
            img.save(test_img_path)

            result = runner.invoke(
                main, [test_img_path, "-o", temp_dir, "--format", "heic"]
            )
            assert result.exit_code == 0
            assert os.path.exists(os.path.join(temp_dir, "test.jpg"))
            assert os.path.exists(os.path.join(temp_dir, "test.heic"))

    def test_directory_processing_reports_progress(self):
        """Test that processing a directory reports each file processed."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            first_path = os.path.join(temp_dir, "first.jpg")
            second_path = os.path.join(temp_dir, "second.png")
            Image.new("RGB", (50, 50), color="blue").save(first_path)
            Image.new("RGBA", (50, 50), color="red").save(second_path)

            result = runner.invoke(main, [temp_dir, "-o", temp_dir])
            assert result.exit_code == 0
            assert "Processed: first.jpg" in result.output
            assert "Processed: second.png" in result.output
            assert "Finished processing directory" in result.output
