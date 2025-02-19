#!/usr/bin/env bash

set -euxo pipefail

IS_DEV=''

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --dev)
      IS_DEV=1
      shift
      ;;
    *)
      echo "Unknown argument: ${1}"
      exit 1
      ;;
  esac
done

BIN='dbus-iface-markdown'

if [ -n "${IS_DEV}" ]; then
  BIN=../public/dbus-iface-markdown/bin/dbus-iface-markdown
fi


"${BIN}" --system --dest org.jfhbrook.plusdeck --out ./docs/dbus/iface.md
