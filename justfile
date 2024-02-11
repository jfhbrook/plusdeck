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

_venv:
  if [ ! -d venv ]; then python3 -m venv venv; . ./venv/bin/activate && pip install pip pip-tools wheel; fi

_clean-venv:
  rm -rf venv

# Install all dependencies
install:
  @just _venv
  @just compile
  . ./venv/bin/activate && pip install -r requirements_dev.txt
  . ./venv/bin/activate && pip install -e .

# Update all dependencies
update:
  @just _venv
  . ./venv/bin/activate && pip install pip pip-tools wheel --upgrade
  @just _clean-compile
  @just install

# Update all dependencies and rebuild the environment
upgrade:
  if [ -d venv ]; then just update && just check && just _upgrade; else just update; fi

_upgrade:
  @just _clean-venv
  @just _venv
  @just _clean-compile
  @just compile
  @just install

# Generate locked requirements files based on dependencies in pyproject.toml
compile:
  . ./venv/bin/activate && python -m piptools compile --resolver=backtracking -o requirements.txt pyproject.toml
  . ./venv/bin/activate && python -m piptools compile --resolver=backtracking --extra=dev -o requirements_dev.txt pyproject.toml

_clean-compile:
  rm -f requirements.txt
  rm -f requirements_dev.txt

#
# Development tooling - linting, formatting, etc
#

# Format with black and isort
format:
  . ./venv/bin/activate &&  black './plusdeck' ./tests
  . ./venv/bin/activate &&  isort --settings-file . './plusdeck' ./tests

# Lint with flake8
lint:
  . ./venv/bin/activate && flake8 './plusdeck' ./tests
  . ./venv/bin/activate && validate-pyproject ./pyproject.toml

# Check type annotations with pyright
check:
  . ./venv/bin/activate && npx pyright@latest

# Run tests with pytest
test:
  . ./venv/bin/activate && pytest -vvv ./tests
  @just _clean-test

# Run integration tests (for what they are)
integration:
  . ./venv/bin/activate && python ./tests/integration.py

_clean-test:
  rm -f pytest_runner-*.egg
  rm -rf tests/__pycache__

# Run tests using tox
tox:
  . ./venv/bin/activate && tox
  @just _clean-tox

_clean-tox:
  rm -rf .tox

#
# Shell and console
#

shell:
  . ./venv/bin/activate && bash

jupyterlab:
  . ./venv/bin/activate && jupyter lab

#
# Documentation
#

# Live generate docs and host on a development webserver
docs:
  . ./venv/bin/activate && mkdocs serve

# Build the documentation
build-docs:
  . ./venv/bin/activate && mkdocs build

#
# Package publishing
#

# Build the package
build:
  . ./venv/bin/activate && python -m build

_clean-build:
  rm -rf dist

# Tag the release in git
tag:
  . ./venv/bin/activate && git tag -a "$(python3 -c 'import toml; print(toml.load(open("pyproject.toml", "r"))["project"]["version"])')" -m "Release $(python3 -c 'import toml; print(toml.load(open("pyproject.toml", "r"))["project"]["version"])')"

# Upload built packages
upload:
  . ./venv/bin/activate && twine upload dist/*

# Build the package and publish it to PyPI
publish: build upload

# Clean up loose files
clean: _clean-venv _clean-compile _clean-test _clean-tox
  rm -rf plusdeck.egg-info
  rm -f plusdeck/*.pyc
  rm -rf plusdeck/__pycache__
