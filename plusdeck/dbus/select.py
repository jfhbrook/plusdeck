"""
Convenience functions for configuring the default bus.

DBus has two buses: the user-level "session bus", and the system-wide "system bus".

The session bus starts for your user when you log in, and doesn't have any particular
access or permissions. This is used for user-scoped services. Examples include audio
servers such as PulseAudio and Pioewire, desktop notification daemons, and the Emacs
daemon.

The system bus is used for services accessible for all users, which persist across
login sessions. These services are typically run with elevated permissions, and
implement access control through many various mechanisms. Examples include networking
daemons such as firewalld and NetworkManager, as well as logging services such as
journald and rsyslog.

The `sdbus` library has the concept of a "default bus". This is the bus that a given
object uses when another value isn't supplied, and is similar to `asyncio`'s default
event loop. Unless otherwise configured, this default bus is the system bus when
started through `systemd`, and the user bus otherwise.

This default isn't necessarily appropriate. In particular, if a service is expected
to be run as a system service (as is typical for the `crystalfontz` service), then
the default bus for the DBus client should be the system bus, unless otherwise
specified.

The functions in this module are used by the client and service CLIs to configure
which bus is used by those programs.
"""

import logging

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    sd_bus_open_system,
    sd_bus_open_user,
    set_default_bus,
)

logger = logging.getLogger(__name__)


def select_session_bus() -> None:
    """
    Select the user session bus as the default bus.
    """

    logger.debug("Selecting the user session bus")
    set_default_bus(sd_bus_open_user())


def select_system_bus() -> None:
    """
    Select the global system bus as the default bus.
    """

    logger.debug("Selecting the system bus")
    set_default_bus(sd_bus_open_system())


def select_default_bus() -> None:
    """
    Log that the standard default bus is being used.
    """

    logger.debug("Selecting the default bus")
