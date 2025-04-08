#!/usr/bin/env bash

from tests.helpers import Cli


def test_listen(dbus_cli, confirm) -> None:
    with dbus_cli.bg("listen", quiet=False):
        confirm("Mess with the Plusdeck. Are events showing up?")


def test_listen_for(dbus_cli: Cli) -> None:
    dbus_cli("listen", "--for", "1.0")
