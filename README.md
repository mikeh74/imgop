# ImageFixer

A Python utility for resizing images and creating thumbnails.

## Features

- Resize images while maintaining aspect ratio
- Create square thumbnails from images
- Process single images or entire directories
- Configurable JPEG quality settings
- Command-line interface and Python API

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/mikeh74/imgop.git
cd imgop

# Install in development mode
make install-dev

# Or install normally
pip install .
```

### Install using pipx from github

```bash
pipx install git+https://github.com/mikeh74/imgop.git
```

## Usage

### Command Line Interface

```bash
# Process a single image
imgop image.jpg

# Process all images in a directory
imgop /path/to/images/

# Specify output directory
imgop image.jpg -o /output/directory/

# Custom quality settings
imgop image.jpg -q 95 -t 80

# Show help
imgop --help
```

### Python API

```python
from imgop import ImageProcessor

# Create processor with default settings
processor = ImageProcessor()

# Or with custom quality settings
processor = ImageProcessor(quality=95, thumbnail_quality=80)

# Process a single image
processor.process_image("input.jpg", "output/")

# Process all images in a directory
processor.process_directory("input_dir/", "output_dir/")

# Process with automatic output path detection
processor.process_path("input.jpg")  # Output to same directory
processor.process_path("input_dir/")  # Output to same directory
```

## Development

This project uses modern Python packaging with `pyproject.toml` and includes:

- **Ruff** for fast linting and formatting
- **pytest** for testing
- **pre-commit** for automated code quality checks
- **Makefile** for common development tasks

### Setup Development Environment

```bash
# Install in development mode with dev dependencies
make install-dev

# Set up pre-commit hooks (automatically done by make dev-setup)
make pre-commit-install

# Run all checks
make check

# Run pre-commit on all files
make pre-commit

# Run tests
make test

# Format code
make format

# Fix auto-fixable linting issues
make fix
```

### Available Make Targets

- `make install` - Install the package
- `make install-dev` - Install in development mode with dev dependencies
- `make lint` - Run ruff linting
- `make format` - Format code with ruff
- `make check` - Run all checks (lint + format check)
- `make pre-commit` - Run pre-commit on all files
- `make pre-commit-install` - Install pre-commit hooks
- `make pre-commit-update` - Update pre-commit hook versions
- `make test` - Run tests
- `make build` - Build the package
- `make clean` - Clean build artifacts

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks include:

- **Standard checks**: trailing whitespace, end-of-file fixer, YAML/TOML validation
- **Ruff**: linting and formatting
- **pyupgrade**: upgrade Python syntax to modern patterns
- **Bandit**: security vulnerability scanning

The hooks run automatically on each commit. To run them manually:

```bash
make pre-commit
```

To skip hooks for a specific commit (not recommended):

```bash
git commit --no-verify -m "commit message"
```

## Requirements

- Python 3.10+
- Pillow (PIL)

## License

MIT License - see LICENSE.txt for details.
