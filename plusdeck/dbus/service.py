import asyncio
import logging
import os
from typing import Optional

import click
from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    request_default_bus_name_async,
)

from plusdeck.cli import LogLevel
from plusdeck.config import GLOBAL_FILE
from plusdeck.dbus.error import handle_dbus_error
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface, load_client

logger = logging.getLogger(__name__)


async def service(config_file: Optional[str] = None) -> DbusInterface:
    """
    Create a configure DBus service with a supplied config file.
    """

    client = await load_client(config_file)
    iface = DbusInterface(client, config_file=config_file)

    logger.debug(f"Requesting bus name {DBUS_NAME}...")
    await request_default_bus_name_async(DBUS_NAME)

    logger.debug("Exporting interface to path /...")

    iface.export_to_dbus("/")

    logger.info(f"Listening on {DBUS_NAME} /")

    return iface


async def serve(config_file: Optional[str] = None) -> None:
    """
    Create and serve configure DBus service with a supplied config file.
    """

    async with handle_dbus_error(logger):
        srv = await service(config_file)

        await srv.closed


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
def main(global_: bool, config_file: str, log_level: LogLevel) -> None:
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

    asyncio.run(serve(file))


if __name__ == "__main__":
    main()
