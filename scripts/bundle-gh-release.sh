#!/usr/bin/env bash

set -euo pipefail

FULL_VERSION="${1}"

tar -czf "plusdeck-${FULL_VERSION}.tar.gz" \
  CHANGELOG.md \
  LICENSE \
  Player.ipynb \
  README.md \
  docs \
  plusdeck \
  plusdeck.spec \
  pyproject.toml \
  pytest.ini \
  requirements.txt \
  requirements_dev.txt \
  setup.cfg \
  systemd \
  tests \
  typings \
  uv.lock
