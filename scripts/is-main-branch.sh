#!/usr/bin/env bash

set -euo pipefail

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "${BRANCH}" 1>&2

[[ "${BRANCH}" == main ]]
