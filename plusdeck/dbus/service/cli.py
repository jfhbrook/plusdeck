import asyncio
import logging
import os
from typing import Optional

import click

from plusdeck.cli import LogLevel
from plusdeck.config import GLOBAL_FILE
from plusdeck.dbus.select import (
    select_default_bus,
    select_session_bus,
    select_system_bus,
)
from plusdeck.dbus.service import serve

logger = logging.getLogger(__name__)


@click.command
@click.option(
    "--global/--no-global",
    "global_",
    default=os.geteuid() == 0,
    help=f"Load the global config file at {GLOBAL_FILE} "
    "(default true when called with sudo)",
)
@click.option(
    "--config-file",
    "-C",
    envvar="PLUSDECK_CONFIG_FILE",
    default=GLOBAL_FILE,
    type=click.Path(),
    help="A path to a config file",
)
@click.option(
    "--log-level",
    envvar="PLUSDECK_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
)
@click.option(
    "--user/--system",
    type=click.BOOL,
    default=None,
    help="Connect to either the user or system bus",
)
def main(
    global_: bool, config_file: str, log_level: LogLevel, user: Optional[bool]
) -> None:
    """
    Expose the Plus Deck 2C PC Cassette Deck as a DBus service.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    file = None
    if config_file:
        if global_:
            logger.debug(
                "--config-file is specified, so --global flag will be ignored."
            )
        file = config_file
    elif global_:
        file = GLOBAL_FILE

    if user:
        select_session_bus()
    elif user is False:
        select_system_bus()
    else:
        select_default_bus()

    asyncio.run(serve(file))


if __name__ == "__main__":
    main()
