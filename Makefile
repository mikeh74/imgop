.PHONY: help install install-dev lint format check test clean build dist upload pre-commit

# Variables
VENV_NAME ?= .venv
PYTHON_ENV_PATH := $(or $(VIRTUAL_ENV), $(VENV_NAME))
PIP = $(PYTHON_ENV_PATH)/bin/pip
RUFF = $(PYTHON_ENV_PATH)/bin/ruff
PYTEST = $(PYTHON_ENV_PATH)/bin/pytest
PRECOMMIT = $(PYTHON_ENV_PATH)/bin/pre-commit

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install the package in development mode with dev dependencies"
	@echo "  lint         - Run ruff linting"
	@echo "  format       - Run ruff formatting"
	@echo "  check        - Run all checks (lint + format check)"
	@echo "  pre-commit   - Run pre-commit on all files"
	@echo "  test         - Run tests with pytest"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  dist         - Create distribution files"
	@echo "  upload       - Upload to PyPI (requires authentication)"

pip_env:
	@# check if PYTHON_ENV = $(VENV_NAME) and if it is then check whether the directory exists
	@-echo "PYTHON_ENV is set to $(PYTHON_ENV_PATH)";
	@-if [ "$(PYTHON_ENV_PATH)" = $(VENV_NAME) ]; then \
		if [ ! -d "$(PYTHON_ENV_PATH)" ]; then \
			python3 -m venv $(VENV_NAME) && $(VENV_NAME)/bin/pip install --upgrade pip; \
			echo "Virtual environment created."; \
		fi; \
	fi

# Create virtual environment if it doesn't exist
.venv/bin/activate: pip_env

# Installation targets
# install: pip_env
# 	$(PIP) install .

# install-dev: pip_env
# 	$(PIP) install -e ".[dev]"

# Pre-commit targets
pre-commit: pre-commit-install
	$(PRECOMMIT) run

# Pre-commit targets
pre-commit-all: pre-commit-install
	$(PRECOMMIT) run --all-files

pre-commit-install:
	$(PIP) install pre-commit
	$(PRECOMMIT) install

pre-commit-update:
	$(PRECOMMIT) autoupdate

# Testing targets
test:
	$(PYTEST)

test-cov:
	$(PYTEST) --cov=imagefixer --cov-report=html --cov-report=term

# Build and distribution targets
clean:
	rm -rf .venv/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

dist: build
	@echo "Distribution files created in dist/"
	@ls -la dist/

# upload: dist
# 	$(PYTHON) -m twine upload dist/*

# Development shortcuts
fix: format
	$(RUFF) check --fix src/ tests/

# dev-setup: install-dev
# 	$(PRE_COMMIT) install
# 	@echo "Development environment set up!"
# 	@echo "Run 'make check' or 'make pre-commit' to verify everything works."
