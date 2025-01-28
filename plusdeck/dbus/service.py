import asyncio

try:
    from sdbus import request_default_bus_name_async  # type: ignore
except ImportError:
    from plusdeck.dbus.shims import request_default_bus_name_async

from plusdeck.dbus.interface import DBUS_NAME, load_client, DbusInterface


async def service() -> DbusInterface:
    client = await load_client()
    iface = DbusInterface(client)

    await request_default_bus_name_async(DBUS_NAME)
    iface.export_to_dbus("/")

    return iface


async def serve() -> None:
    srv = await service()

    await srv.closed


# TODO: click entry point with a --global flag
def main() -> None:
    # Assert the import works
    import sdbus  # noqa: F401 # type: ignore

    asyncio.run(serve())
