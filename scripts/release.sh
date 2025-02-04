#!/usr/bin/env bash

VERSION="${1}"
PATCH="${2}"

NOTES="$(./scripts/changelog-entry.py "${VERSION}")"

gh release create "plusdeck-${VERSION}-${PATCH}" \
  -t "plusdeck v${VERSION}" \
  -n "${NOTES}" \
  "plusdeck-${VERSION}.tar.gz"
