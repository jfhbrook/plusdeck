#!/usr/bin/env bash

VERSION="${1}"
RELEASE="${2}"

NOTES="$(./scripts/changelog-entry.py "${VERSION}")"

gh release create "plusdeck-${VERSION}-${RELEASE}" \
  -t "plusdeck v${VERSION}" \
  -n "${NOTES}" \
  "plusdeck-${VERSION}.tar.gz"
