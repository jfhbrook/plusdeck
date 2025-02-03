import asyncio
import logging
from typing import Optional, Self

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
    DbusInterfaceCommonAsync,
)

from plusdeck.client import Client, create_connection, Receiver, State
from plusdeck.config import Config
from plusdeck.dbus.config import ConfigStruct

logger = logging.getLogger(__name__)

DBUS_NAME = "org.jfhbrook.plusdeck"


async def load_client(config_file: str) -> Client:
    config: Config = Config.from_file(config_file)

    client = await create_connection(config.port)

    return client


class DbusInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):
    """
    A DBus interface for controlling the Plus Deck 2C PC Cassette Deck.
    """

    def __init__(self: Self, config_file: str, client: Client) -> None:
        super().__init__()
        self._config: Config = Config.from_file(config_file)
        self.client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self._rcv: Optional[Receiver] = None
        self._current_state: State = State.UNSUBSCRIBED
        self.subscribe()

    @dbus_property_async("(ss)")
    def config(self: Self) -> ConfigStruct:
        """
        The DBus service's currently loaded configuration.
        """

        return (self._config.file or "", self._config.port)

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
                self._current_state = state
                self.state.emit(state.name)  # type: ignore
            except TimeoutError:
                pass

    async def close(self: Self) -> None:
        """
        Unsubscribe from events and close the client.
        """

        async with self._client_lock:
            await self.client.unsubscribe()

            self._rcv = None
            await self._subscription
            self.client.close()
            await self.client.closed

    @property
    def closed(self: Self) -> asyncio.Future:
        """
        A Future that resolves when the client is closed.
        """

        return self.client.closed

    @dbus_method_async("")
    async def play_a(self: Self) -> None:
        """
        Play side A.
        """
        self.client.play_a()

    @dbus_method_async("")
    async def play_b(self: Self) -> None:
        """
        Play side B.
        """

        self.client.play_b()

    @dbus_method_async("")
    async def fast_forward_a(self: Self) -> None:
        """
        Fast-forward side A.
        """

        self.client.fast_forward_a()

    @dbus_method_async("")
    async def fast_forward_b(self: Self) -> None:
        """
        Fast-forward side B.
        """

        self.client.fast_forward_b()

    @dbus_method_async("")
    async def rewind_a(self: Self) -> None:
        """
        Rewind side A. Equivalent to fast-forwarding side B.
        """

        self.client.rewind_a()

    @dbus_method_async("")
    async def rewind_b(self: Self) -> None:
        """
        Rewind side B. Equivalent to fast-forwarding side A.
        """

        self.client.rewind_b()

    @dbus_method_async("")
    async def pause(self: Self) -> None:
        """
        Pause if playing, or start playing if paused.
        """

        self.client.pause()

    @dbus_method_async("")
    async def stop(self: Self) -> None:
        """
        Stop the tape.
        """

        self.client.stop()

    @dbus_method_async("")
    async def eject(self: Self) -> None:
        """
        Eject the tape.
        """

        self.client.eject()

    @dbus_method_async("sd", "b")
    async def wait_for(self: Self, state: str, timeout: float) -> bool:
        """
        Wait for an expected state, with an optional timeout. When timeout is negative,
        it will be ignored.
        """

        ok = True

        st = State[state]
        to = timeout if timeout >= 0 else None

        try:
            await self.client.wait_for(st, to)
        except TimeoutError:
            ok = False

        return ok

    @dbus_property_async("s")
    def current_state(self: Self) -> str:
        """
        Get the last known state of the Plus Deck 2C PC Cassette Deck.
        """
        return self._current_state.name

    @dbus_signal_async("s")
    def state(self: Self) -> str:
        """
        Listen for updates to the state of the Plus Deck 2C Cassette Deck.
        """

        raise NotImplementedError("state")
