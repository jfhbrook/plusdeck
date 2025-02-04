#!/usr/bin/env bash

LINES="$(git status --porcelain)"

echo "${LINES}" 1>&2

[ -z "${LINES}" ]
