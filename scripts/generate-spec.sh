#!/usr/bin/env bash

VERSION="${1}"
PATCH="${2}"

export VERSION
export PATCH

gomplate -f ./plusdeck.spec.tmpl -o plusdeck.spec
