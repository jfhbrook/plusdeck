#!/usr/bin/env bash

from tests.helpers import Cli


def test_subscribe(dbus_cli, confirm) -> None:
    with dbus_cli.bg("subscribe", quiet=False):
        confirm("Mess with the Plusdeck. Are events showing up?")


def test_subscribe_for(dbus_cli: Cli) -> None:
    dbus_cli("subscribe", "--for", "1.0")
