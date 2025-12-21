"""Tests for the CLI module."""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from imgop.cli import create_parser, main, validate_args


class TestCLI:
    """Test cases for CLI functionality."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "imgop"

    def test_parser_required_args(self):
        """Test parser with required arguments."""
        parser = create_parser()
        args = parser.parse_args(["test_image.jpg"])
        assert args.path == "test_image.jpg"
        assert args.output is None
        assert args.quality == 85
        assert args.thumbnail_quality == 70

    def test_parser_all_args(self):
        """Test parser with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            ["test_image.jpg", "-o", "/output/", "-q", "95", "-t", "80"]
        )
        assert args.path == "test_image.jpg"
        assert args.output == "/output/"
        assert args.quality == 95
        assert args.thumbnail_quality == 80

    def test_validate_args_valid(self):
        """Test argument validation with valid values."""
        args = argparse.Namespace(quality=85, thumbnail_quality=70)
        # Should not raise any exception
        validate_args(args)

    def test_validate_args_invalid_quality(self):
        """Test argument validation with invalid quality."""
        args = argparse.Namespace(quality=101, thumbnail_quality=70)
        with pytest.raises(ValueError, match="Quality must be between 1 and 100"):
            validate_args(args)

    def test_validate_args_invalid_thumbnail_quality(self):
        """Test argument validation with invalid thumbnail quality."""
        args = argparse.Namespace(quality=85, thumbnail_quality=0)
        with pytest.raises(
            ValueError, match="Thumbnail quality must be between 1 and 100"
        ):
            validate_args(args)

    def test_main_file_not_found(self):
        """Test main function with nonexistent file."""
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            result = main(["nonexistent.jpg"])
            assert result == 1
            assert "Error:" in fake_stderr.getvalue()

    def test_main_invalid_quality(self):
        """Test main function with invalid quality."""
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            result = main(["test.jpg", "-q", "101"])
            assert result == 1
            assert "Error:" in fake_stderr.getvalue()

    @patch("imagefixer.cli.ImageProcessor")
    def test_main_success(self, mock_processor):
        """Test successful execution of main function."""
        mock_instance = mock_processor.return_value
        mock_instance.process_path.return_value = None

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            result = main(["test.jpg"])
            assert result == 0
            assert "Successfully processed" in fake_stdout.getvalue()
            mock_processor.assert_called_once_with(quality=85, thumbnail_quality=70)
            mock_instance.process_path.assert_called_once_with("test.jpg", None)
