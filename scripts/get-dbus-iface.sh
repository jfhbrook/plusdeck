#!/usr/bin/env bash

function extract-response {
  tail -n +2 | sed 's/^\s*string "//' | sed 's/"$//'
}

dbus-send --system \
  --dest=org.jfhbrook.plusdeck "/" \
  --print-reply \
  org.freedesktop.DBus.Introspectable.Introspect \
  | extract-response
