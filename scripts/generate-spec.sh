#!/usr/bin/env bash

set -euo pipefail

VERSION="${1}"
RELEASE="${2}"

export VERSION
export RELEASE

gomplate -f ./plusdeck.spec.tmpl -o plusdeck.spec
