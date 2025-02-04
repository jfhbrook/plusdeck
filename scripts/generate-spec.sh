#!/usr/bin/env bash

VERSION="${1}"
RELEASE="${2}"

export VERSION
export RELEASE

gomplate -f ./plusdeck.spec.tmpl -o plusdeck.spec
