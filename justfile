set dotenv-load := true

# Generally this is '1', but may be incremented if a versioned package release
# is broken.
PATCH := "1"

# By default, run checks and tests, then format and lint
default:
  if [ ! -d venv ]; then just install; fi
  @just format
  @just check
  @just test
  @just lint

#
# Installing, updating and upgrading dependencies
#

venv:
  if [ ! -d .venv ]; then uv venv; fi

clean-venv:
  rm -rf .venv

# Install all dependencies
install:
  @just venv
  if [[ "$(uname -s)" == Linux ]]; then uv sync --dev --extra dbus; else uv sync --dev; fi
  uv pip install -e .

# Update all dependencies
update:
  @just install

# Update all dependencies and rebuild the environment
upgrade:
  if [ -d venv ]; then just update && just check && just _upgrade; else just update; fi

_upgrade:
  @just clean-venv
  @just venv
  @just install

# Generate locked requirements files based on dependencies in pyproject.toml
compile:
  uv pip compile -o requirements.txt pyproject.toml
  cp requirements.txt requirements_dev.txt
  python3 -c 'import toml; print("\n".join(toml.load(open("pyproject.toml"))["dependency-groups"]["dev"]))' >> requirements_dev.txt

clean-compile:
  rm -f requirements.txt
  rm -f requirements_dev.txt

#
# Running the CLI
#

# Run a command or script
run *argv:
  uv run {{ argv }}

# Run the plusdeck cli
start *argv:
  uv run -- plusdeck {{ argv }}

#
# Development tooling - linting, formatting, etc
#

# Format with black and isort
format:
  uv run black './plusdeck' ./tests
  uv run isort --settings-file . './plusdeck' ./tests

# Lint with flake8
lint:
  uv run flake8 './plusdeck' ./tests
  uv run validate-pyproject ./pyproject.toml

# Check type annotations with pyright
check:
  uv run npx pyright@latest

# Run tests with pytest
test:
  uv run pytest -vvv ./tests
  @just clean-test

# Update snapshots
snap:
  uv run pytest --snapshot-update ./tests
  @just clean-test

# Run integration tests (for what they are)
integration:
  uv run python ./tests/integration.py

clean-test:
  rm -f pytest_runner-*.egg
  rm -rf tests/__pycache__

# Run tests using tox
tox:
  uv run tox
  @just _clean-tox

clean-tox:
  rm -rf .tox

#
# Shell and console
#

shell:
  uv run bash

jupyterlab:
  uv run jupyter lab

#
# Documentation
#

# Live generate docs and host on a development webserver
docs:
  uv run mkdocs serve

# Build the documentation
build-docs:
  uv run mkdocs build

#
# Package publishing
#

#
# Package publishing
#

# Build the package
build:
  uv build

# Clean the build
clean-build:
  rm -rf dist

# Generate plusdeck.spec
generate-spec:
  ./scripts/generate-spec.sh "$(./scripts/version.py)" '{{ PATCH }}'

# Update the package version in ./copr/python-plusdeck.yml
copr-update-version:
  VERSION="$(./scripts/version.py)" yq -i '.spec.packageversion = strenv(VERSION)' copr/python-plusdeck.yml

# Fail if there are uncommitted files
check-dirty:
  ./scripts/is-dirty.sh

# Fail if not on the main branch
check-main-branch:
  ./scripts/is-main-branch.sh

# Tag the release with tito
tag:
  tito tag --use-version "$(./scripts/version.py)"

# Bundle the package for GitHub release
bundle-release:
  ./scripts/bundle.sh "$(./scripts/version.py)"

# Clean up the release package
clean-release:
  rm -f "plusdeck-$(./scripts/version.py).tar.gz"

# Push main and tags
push:
  git push origin main --follow-tags

# Publish package to PyPI
publish-pypi: build
  uv publish -u __token__

# Create a GitHub release
gh-release:
  bash ./scripts/release.sh "$(python ./scripts/get-version.py)" '{{ PATCH }}'

# Apply a COPR package configuration
apply-copr package:
  coprctl apply -f ./copr/{{ package }}.yml

# Build a COPR package
build-copr package:
  copr build-package jfhbrook/joshiverse --name '{{ package }}'

# Publish the release on PyPI, GitHub and Copr
publish:
  # Update requirements files
  @just compile
  # Update versions to match pyproject.toml
  @just generate-spec
  @just copr-update-version
  # Ensure git is in a good state
  @just check-main-branch
  @just check-dirty
  # Tag and push
  @just tag
  @just push
  # Build package and bundle release
  @just clean-build
  @just clean-release
  @just build
  @just bundle-release
  # Publish package and release
  @just gh-release
  @just publish-pypi
  # Update packages on COPR
  @just apply-copr python-plusdeck
  @just apply-copr plusdeck
  @just build-copr python-plusdeck
  @just build-copr plusdeck

# Clean up loose files
clean: clean-venv clean-compile clean-test clean-build clean-release clean-tox
  rm -rf plusdeck.egg-info
  rm -f plusdeck/*.pyc
  rm -rf plusdeck/__pycache__
