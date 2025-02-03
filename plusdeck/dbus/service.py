import asyncio
import logging

import click
from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    request_default_bus_name_async,
)

from plusdeck.cli import LogLevel
from plusdeck.config import GLOBAL_FILE
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface, load_client

logger = logging.getLogger(__name__)


async def service(config_file: str) -> DbusInterface:
    """
    Create a configure DBus service with a supplied config file.
    """

    client = await load_client(config_file)
    iface = DbusInterface(config_file, client)

    logger.debug(f"Requesting bus name {DBUS_NAME}...")
    await request_default_bus_name_async(DBUS_NAME)

    logger.debug("Exporting interface to path /...")

    iface.export_to_dbus("/")

    logger.info(f"Listening on {DBUS_NAME} /")

    return iface


async def serve(config_file: str) -> None:
    """
    Create and serve configure DBus service with a supplied config file.
    """

    srv = await service(config_file)

    await srv.closed


@click.command
@click.option(
    "--config-file",
    "-C",
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
def main(config_file: str, log_level: LogLevel) -> None:
    """
    Expose the Plus Deck 2C PC Cassette Deck as a DBus service.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    asyncio.run(serve(config_file))


if __name__ == "__main__":
    main()
