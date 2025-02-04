#!/usr/bin/env bash

VERSION="${1}"

tar -czf "plusdeck-${VERSION}.tar.gz" \
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
  tox.ini \
  typings \
  uv.lock
