set dotenv-load := true

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
  uv run black './plusdeck' ./tests ./scripts
  uv run isort --settings-file . './plusdeck' ./tests ./scripts

# Lint with flake8
lint:
  uv run flake8 './plusdeck' ./tests ./scripts
  uv run validate-pyproject ./pyproject.toml
  shellcheck ./scripts/*.sh

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

# Install systemd service files for development purposes
install-service:
  sudo install -p -D -m 0644 systemd/plusdeck.service /usr/lib/systemd/system/plusdeck.service
  sudo install -p -D -m 0644 dbus/org.jfhbrook.plusdeck.conf /etc/dbus-1/system.d/org.jfhbrook.plusdeck.conf

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

# Build the package
build:
  uv build

# Clean the build
clean-build:
  rm -rf dist

# Generate plusdeck.spec
generate-spec:
  ./scripts/generate-spec.sh "$(./scripts/version.py)" "$(./scripts/release-version.py)"

# Update the package version in ./copr/python-plusdeck.yml
copr-update-version:
  VERSION="$(./scripts/version.py)" yq -i '.spec.packageversion = strenv(VERSION)' ./copr/python-plusdeck.yml

# Commit generated files
commit-generated-files:
  git add requirements.txt
  git add requirements_dev.txt
  git add plusdeck.spec
  git add ./copr
  git commit -m 'Update generated files' || echo 'No changes to files'

# Fail if there are uncommitted files
check-dirty:
  ./scripts/is-dirty.sh

# Fail if not on the main branch
check-main-branch:
  ./scripts/is-main-branch.sh

# Tag the release with tito
tag:
  ./scripts/tag.sh

# Bundle the package for GitHub release
bundle-gh-release:
  ./scripts/bundle-gh-release.sh "$(./scripts/version.py)-$(./scripts/release-version.py)"

# Clean up the release package
clean-release:
  rm -f "plusdeck-*-*.tar.gz"

# Push main and tags
push:
  git push origin main --follow-tags

# Publish package to PyPI
publish-pypi: build
  uv publish -t "$(op item get 'PyPI' --fields 'API Token' --reveal)"

# Create a GitHub release
gh-release:
  bash ./scripts/gh-release.sh "$(python ./scripts/version.py)-$(python ./scripts/release-version.py)"

# Apply a COPR package configuration
apply-copr package:
  coprctl apply -f ./copr/{{ package }}.yml

# Build a COPR package
build-copr package:
  copr build-package jfhbrook/joshiverse --name '{{ package }}'

# Publish the release on PyPI, GitHub and Copr
publish:
  # Generate files and commit
  @just compile
  @just generate-spec
  @just copr-update-version
  @just commit-generated-files
  # Ensure git is in a good state
  @just check-main-branch
  @just check-dirty
  # Tag and push
  @just tag
  @just push
  # Build package and bundle release
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just clean-build; fi
  @just clean-release
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just build; fi
  @just bundle-gh-release
  # Publish package and release
  @just gh-release
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just publish-pypi; fi
  # Update packages on COPR
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just apply-copr python-plusdeck; fi
  @just apply-copr plusdeck
  if [[ "$(./scripts/release-version.y)" == '1' ]]; then just build-copr python-plusdeck; fi
  @just build-copr plusdeck

# Clean up loose files
clean: clean-venv clean-compile clean-test clean-build clean-release clean-tox
  rm -rf plusdeck.egg-info
  rm -f plusdeck/*.pyc
  rm -rf plusdeck/__pycache__
