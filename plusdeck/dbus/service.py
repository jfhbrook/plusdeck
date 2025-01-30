import asyncio

import click

from sdbus import request_default_bus_name_async
from plusdeck.config import GLOBAL_FILE
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface, load_client


async def service(config_file: str) -> DbusInterface:
    client = await load_client(config_file)
    iface = DbusInterface(config_file, client)

    await request_default_bus_name_async(DBUS_NAME)
    iface.export_to_dbus("/")

    return iface


async def serve(config_file: str) -> None:
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
def main(config_file: str) -> None:
    # Assert the import works
    import sdbus  # noqa: F401 # type: ignore

    asyncio.run(serve(config_file))
