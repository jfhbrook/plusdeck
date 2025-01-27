import asyncio

try:
    from sdbus import request_default_bus_name_async  # type: ignore
except ImportError:
    from plusdeck.dbus.shims import request_default_bus_name_async

from plusdeck.dbus.interface import DBUS_NAME, load_client, PlusdeckInterface


async def service() -> PlusdeckInterface:
    client = await load_client()
    iface = PlusdeckInterface(client)

    await request_default_bus_name_async(DBUS_NAME)
    iface.export_to_dbus("/")

    return iface


async def serve() -> None:
    srv = await service()

    await srv.closed


def main() -> None:
    # Assert the import works
    import sdbus  # noqa: F401 # type: ignore

    asyncio.run(serve())
