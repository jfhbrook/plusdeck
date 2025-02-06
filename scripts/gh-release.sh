#!/usr/bin/env bash

set -euo pipefail

FULL_VERSION="${1}"

NOTES="$(./scripts/changelog-entry.py "${FULL_VERSION}")"

gh release create "plusdeck-${FULL_VERSION}" \
  -t "plusdeck v${FULL_VERSION}" \
  -n "${NOTES}" \
  "plusdeck-${FULL_VERSION}.tar.gz"
