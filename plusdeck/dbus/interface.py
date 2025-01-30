import asyncio
from typing import Optional, Self

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
    DbusInterfaceCommonAsync,
)

from plusdeck.client import Client, create_connection, Receiver, State
from plusdeck.config import Config

DBUS_NAME = "org.jfhbrook.plusdeck"


async def load_client(config_file: str) -> Client:
    config: Config = Config.from_file(config_file)

    client = await create_connection(config.port)

    return client


class DbusInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):

    def __init__(self: Self, config_file: str, client: Client) -> None:
        super().__init__()
        self._config_file = config_file
        self._client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self._rcv: Optional[Receiver] = None
        self.subscribe()

    @dbus_property_async("s")
    def config_file(self: Self) -> str:
        return self._config_file

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

    async def _closed(self: Self) -> None:
        # Shenanigans to allow for a refresh that replaces the client
        client = self.client
        while not client.closed.done():
            await client.closed
            client = self.client

    @property
    def closed(self: Self) -> asyncio.Future:
        return asyncio.ensure_future(self._closed())

    @dbus_method_async()
    async def reload(self: Self) -> None:
        async with self._client_lock:
            await self._close(reloading=True)
            self.client = await load_client(self._config_file)
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

    @dbus_method_async("sf")
    async def wait_for(self: Self, state: str, timeout: float) -> None:
        st = State[state]
        to = timeout if timeout > 0 else None

        await self.client.wait_for(st, to)

    @dbus_signal_async("s")
    def state(self: Self) -> str:
        raise NotImplementedError("state")
