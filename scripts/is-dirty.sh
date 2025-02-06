#!/usr/bin/env bash

set -euo pipefail

LINES="$(git status --porcelain)"

echo "${LINES}" 1>&2

[ -z "${LINES}" ]
