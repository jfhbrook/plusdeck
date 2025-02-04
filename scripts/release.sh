#!/usr/bin/env bash

VERSION="${1}"
PATCH="${2}"

NOTES=''
TAKE_NOTES=''

while read line; do
  if [[ "${line}" == '%changelog' ]]; then
    TAKE_NOTES=1
  elif [ -n "${TAKE_NOTES}" ]; then
    if [ -z "${line}" ]; then
      break
    fi
    NOTES="${NOTES}
${line}"
  fi
done < plusdeck.spec

gh release create "plusdeck-${VERSION}-${PATCH}" \
  -t "plusdeck v${VERSION}" \
  -n "${NOTES}" \
  "plusdeck-${VERSION}.tar.gz"
