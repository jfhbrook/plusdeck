#!/usr/bin/env bash

set -euo pipefail

VERSION="$(./scripts/version.py)"
RELEASE="$(./scripts/release-version.py)"
FULL_VERSION="${VERSION}-${RELEASE}"

tito tag --use-version "${VERSION}" \
         --use-release "${RELEASE}" \
         --changelog="$(./scripts/changelog-entry.py "${FULL_VERSION}" | sed 's/^/  /')"
