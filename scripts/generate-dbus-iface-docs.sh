#!/usr/bin/env bash

dbus-send --system --dest=org.jfhbrook.plusdeck --print-reply "/" org.freedesktop.DBus.Introspectable.Introspect
