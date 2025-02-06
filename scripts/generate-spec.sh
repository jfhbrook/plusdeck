#!/usr/bin/env bash

set -euo pipefail

VERSION="${1}"
RELEASE="${2}"
CHANGELOG="$(./scripts/spec-changelog.py)"

export VERSION
export RELEASE
export CHANGELOG

gomplate -f ./plusdeck.spec.tmpl -o plusdeck.spec
