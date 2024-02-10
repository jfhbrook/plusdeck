# -*- coding: utf-8 -*-

import asyncio
from collections.abc import AsyncGenerator
from enum import Enum
from typing import Callable, Iterable, Optional, Set, Union

from pyee.asyncio import AsyncIOEventEmitter
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

"""
A client library for the Plus Deck 2C PC Cassette Deck.
"""


class Command(Enum):
    """A command for the Plus Deck 2C PC Cassette Deck."""

    PlaySideA = b"\x01"
    PlaySideB = b"\x02"
    FastForward = b"\x03"
    Rewind = b"\x04"
    TogglePause = b"\x05"
    Stop = b"\x06"
    Eject = b"\x08"
    Listen = b"\x0b"
    Close = b"\x0c"


class State(Enum):
    """The state of the Plus Deck 2C PC Cassette Deck."""

    PlayingA = 0x0A
    PausedOnB = 0x0C
    PlayingB = 0x14
    Ready = 0x15
    PausedOnA = 0x16
    FastForwarding = 0x1E
    Rewinding = 0x28
    Stopped = 0x32
    Ejected = 0x3C
    Closed = 0x00


class Side(Enum):
    """A side of a cassette."""

    A = "A"
    B = "B"


class ConnectionError(Exception):
    """A connection error."""

    pass


class StateError(ValueError):
    """A state error."""

    code: int

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


Handler = Callable[[State], None]
StateHandler = Callable[[], None]


class Receiver(asyncio.Queue):
    """Receive state change events from the Plus Deck 2C PC Cassette Deck."""

    _client: "Client"

    def __init__(self, client: "Client", maxsize=0):
        super().__init__(maxsize)
        self._client = client

    async def __aiter__(self) -> AsyncGenerator[State, None]:
        """Iterate over state change events."""

        while True:
            state = await self.get()

            yield state

            if state == State.Closed:
                self.close()
                break

    def close(self) -> None:
        """Close the receiver."""
        self._client._receivers.remove(self)


class Client(asyncio.Protocol):
    """A client for the Plus Deck 2C PC Cassette Deck."""

    state: State
    events: AsyncIOEventEmitter
    _loop: asyncio.AbstractEventLoop
    _transport: SerialTransport | None
    _sent_close: bool
    _connection_made: asyncio.Future[None]
    _receivers: Set[Receiver]

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        _loop = loop if loop else asyncio.get_running_loop()

        self.state = State.Closed
        self.events = AsyncIOEventEmitter(_loop)
        self._loop = _loop
        self._sent_close = False
        self._online = self._loop.create_future()

    def connection_made(self, transport: asyncio.BaseTransport):
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._connection_made.set_result(None)

    def send(self, command: Command):
        """Send a command to the Plus Deck 2C."""

        if not self._transport:
            raise ConnectionError("Connection has not yet been made.")

        self._transport.write(command.value)

        if command == Command.Close:
            self._sent_close = True
        else:
            self._sent_close = False

    def data_received(self, data):
        for code in data:
            try:
                state = State(code)
            except ValueError:
                raise StateError(f"Unknown state: {code}", code)
            else:
                self._on_state(state)

    def _on_state(self, state: State):
        previous = self.state

        # When turning off, what I've observed is that we always receive
        # exactly one pause event. I'm not entirely sure it's reliable, but
        # until it's disproven I'm treating it as such.
        #
        # If it turns out the single event is unspecified, then the logic may
        # simply be modified to handle any event. If, however, it turns out
        # there are an unspecified number of events, we will need to resort to
        # timeouts.

        sent_close = self._sent_close
        self._sent_close = False

        if sent_close and (state == State.PausedOnA or state == State.PausedOnB):
            state = State.Closed

        self.state = state

        # Emit the state every time
        self.events.emit("state", state)

        # Only receive state changes
        if state != previous:
            for rcv in self._receivers:
                self._loop.create_task(rcv.put(state))

    def on(self, state: State, f: StateHandler) -> Handler:
        """Call an event handler on a given state."""

        return self.listens_to(state)(f)

    def listens_to(self, state: State) -> Callable[[StateHandler], Handler]:
        """Decorate an event handler to be called on a given state."""

        want = state

        def decorator(f: StateHandler) -> Handler:
            def handler(state: State) -> None:
                if state == want:
                    f()

            return self.events.add_listener("state", handler)

        return decorator

    def once(self, state: State, f: StateHandler) -> Handler:
        """Call an event handler on a given state once."""

        return self.listens_once(state)(f)

    def listens_once(self, state: State) -> Callable[[StateHandler], Handler]:
        """Decorate an event handler to be called once a given state occurs."""

        want = state

        def decorator(f: StateHandler) -> Handler:
            def handler(state: State) -> None:
                if state == want:
                    f()
                    self.events.remove_listener("state", handler)

            return self.events.add_listener("state", handler)

        return decorator

    def wait_for(
        self, state: State, timeout: Optional[int] = None
    ) -> asyncio.Future[None]:
        """Wait for a given state to emit."""

        fut = asyncio.ensure_future(
            asyncio.wait_for(self._loop.create_future(), timeout=timeout)
        )

        @self.listens_once(state)
        def listener() -> None:
            fut.set_result(None)

        self.events.on("state", listener)

        return fut

    async def listen(self, maxsize: int = 0) -> Receiver:
        """Listen for state changes."""

        rcv = Receiver(client=self, maxsize=maxsize)
        self._receivers.add(rcv)

        if self.state == State.Closed:
            self.send(Command.Listen)
            await self.wait_for(State.Ready)
            self.events.emit("listen")

        return rcv

    def receivers(self) -> Iterable[Receiver]:
        """Currently active receivers."""

        return self._receivers

    async def close(self) -> None:
        """Stop listening for state changes."""

        self.send(Command.Close)

        @self.listens_once(State.Closed)
        def listener():
            self.events.emit("close")


async def create_connection(
    url: str,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Client:
    _loop = loop if loop else asyncio.get_running_loop()

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(_loop),
        url,
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
    )

    await client._online

    return client
