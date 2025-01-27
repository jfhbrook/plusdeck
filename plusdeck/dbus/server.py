import asyncio
from typing import Any, Optional, Type

try:
    from typing import Self
except ImportError:
    Self = Any

try:
    from sdbus import (  # type: ignore
        dbus_method_async,
        dbus_signal_async,
        DbusInterfaceCommonAsync,
        request_default_bus_name_async,
    )
except ImportError:

    def dbus_method_async(*args, **kwargs) -> Any:
        def decorator(f: Any) -> Any:
            return f

        return decorator

    def dbus_signal_async(*args, **kwargs) -> Any:
        def decorator(f: Any) -> Any:
            return f

        return decorator

    class DbusInterfaceCommonAsync:
        def __init_subclass__(cls: Type[Self], *args, **kwargs) -> None:
            pass

        def export_to_dbus(self: Self, path: str) -> None:
            pass

    async def request_default_bus_name_async(bus_name: str) -> None:
        pass


from plusdeck.client import Client, create_connection, Receiver, State
from plusdeck.config import Config

DBUS_NAME = "org.jfhbrook.plusdeck"


async def load_client() -> Client:
    config: Config = Config.from_file(load_environment=True)

    client = await create_connection(config.port)

    return client


class PlusdeckInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):
    def __init__(self: Self, client: Client) -> None:
        super().__init__()
        self._client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self._rcv: Optional[Receiver] = None
        self.subscribe()

    def subscribe(self: Self) -> None:
        self._subscription = asyncio.create_task(self.subscription())

    async def subscription(self: Self) -> None:
        if not self._rcv:
            self._rcv: Optional[Receiver] = await self.client.subscribe()

        while True:
            if not self._rcv:
                break
            try:
                state: State = await self._rcv.get_state()
                self.state.emit(state.name)  # type: ignore
            except TimeoutError:
                pass

    async def close(self: Self) -> None:
        async with self._client_lock:
            await self._close()

    async def _close(self: Self, reloading=False) -> None:
        client = self.client

        if not reloading:
            await client.unsubscribe()

        self._rcv = None
        await self._subscription
        client.close()
        await client.closed

    @dbus_method_async()
    async def reload(self: Self) -> None:
        async with self._client_lock:
            await self._close(reloading=True)
            self.client = await load_client()
            self.subscribe()

    @dbus_method_async()
    async def play_a(self: Self) -> None:
        """
        Play side A.
        """
        self.client.play_a()

    @dbus_method_async()
    async def play_b(self: Self) -> None:
        """
        Play side B.
        """

        self.client.play_b()

    @dbus_method_async()
    async def fast_forward_a(self: Self) -> None:
        """
        Fast-forward side A.
        """

        self.client.fast_forward_a()

    @dbus_method_async()
    async def fast_forward_b(self: Self) -> None:
        """
        Fast-forward side B.
        """

        self.client.fast_forward_b()

    @dbus_method_async()
    async def rewind_a(self: Self) -> None:
        """
        Rewind side A. Equivalent to fast-forwarding side B.
        """

        self.client.rewind_a()

    @dbus_method_async()
    async def rewind_b(self: Self) -> None:
        """
        Rewind side B. Equivalent to fast-forwarding side A.
        """

        self.client.rewind_b()

    @dbus_method_async()
    async def pause(self: Self) -> None:
        """
        Pause if playing, or start playing if paused.
        """

        self.client.pause()

    @dbus_method_async()
    async def stop(self: Self) -> None:
        """
        Stop the tape.
        """

        self.client.stop()

    @dbus_method_async()
    async def eject(self: Self) -> None:
        """
        Eject the tape.
        """

        self.client.eject()

    @dbus_signal_async("s")
    def state(self: Self) -> str:
        raise NotImplementedError("state")


async def server() -> None:
    client = await load_client()

    iface = PlusdeckInterface(client)

    await request_default_bus_name_async(DBUS_NAME)
    iface.export_to_dbus("/")

    await client.closed


def main() -> None:
    # Assert the import works
    import sdbus  # noqa: F401 # type: ignore

    asyncio.run(server())
