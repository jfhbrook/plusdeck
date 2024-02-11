# -*- coding: utf-8 -*-

import asyncio
from collections.abc import AsyncGenerator
from enum import Enum
from typing import Callable, List, Optional, Set, Type

from pyee.asyncio import AsyncIOEventEmitter
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

"""
A client library for the Plus Deck 2C PC Cassette Deck.
"""


class Command(Enum):
    """A command for the Plus Deck 2C PC Cassette Deck."""

    PlayA = b"\x01"
    PlayB = b"\x02"
    FastForward = b"\x03"
    Rewind = b"\x04"
    TogglePause = b"\x05"
    Stop = b"\x06"
    Eject = b"\x08"
    Broadcast = b"\x0b"
    Silence = b"\x0c"


class State(Enum):
    """The state of the Plus Deck 2C PC Cassette Deck."""

    PlayingA = 0x0A
    PausedB = 0x0C
    PlayingB = 0x14
    Ready = 0x15
    PausedA = 0x16
    FastForwarding = 0x1E
    Rewinding = 0x28
    Stopped = 0x32
    Ejected = 0x3C
    Waiting = -1
    Silencing = -2
    Silenced = -3

    @classmethod
    def from_bytes(cls: Type["State"], buffer: bytes) -> List["State"]:
        return [cls(code) for code in buffer]

    @classmethod
    def from_byte(cls: Type["State"], buffer: bytes) -> "State":
        assert len(buffer) == 1, "Can not convert multiple bytes to a single State"
        return cls.from_bytes(buffer)[0]

    def to_bytes(self: "State") -> bytes:
        if self.value < 0:
            raise ValueError(f"Can not convert {self} to bytes")
        return self.value.to_bytes()


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

            # TODO: Should iterator emit silenced state?
            if state != State.Silenced:
                yield state
                continue

            break

    def unsubscribe(self) -> None:
        """Unsubscribe from state changes."""
        try:
            self._client._receivers.remove(self)
        except KeyError:
            pass


class Client(asyncio.Protocol):
    """A client for the Plus Deck 2C PC Cassette Deck."""

    state: State
    events: AsyncIOEventEmitter
    _loop: asyncio.AbstractEventLoop
    _transport: SerialTransport | None
    _connection_made: asyncio.Future[None]
    _receivers: Set[Receiver]

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        _loop = loop if loop else asyncio.get_running_loop()

        self.state = State.Silenced
        self.events = AsyncIOEventEmitter(_loop)
        self._loop = _loop
        self._connection_made = self._loop.create_future()
        self._receivers = set()

    def connection_made(self, transport: asyncio.BaseTransport):
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._connection_made.set_result(None)

    def send(self, command: Command):
        """Send a command to the Plus Deck 2C."""

        if not self._transport:
            raise ConnectionError("Connection has not yet been made.")

        if command == Command.Broadcast:
            self._on_state(State.Waiting)
        elif command == Command.Silence:
            self._on_state(State.Silencing)

        self._transport.write(command.value)

    def data_received(self, data):
        for state in State.from_bytes(data):
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

        if (previous == State.Silencing) and (
            state == State.PausedA or state == State.PausedB
        ):
            state = State.Silenced

        # TODO: If we were silencing and it didn't silence, should we throw
        # an error?

        self.state = state

        if state == State.Ready:
            self.events.emit("ready")

        # Emit the state every time
        self.events.emit("state", state)

        # Only receive state changes
        if state != previous:
            for rcv in self._receivers:
                self._loop.create_task(rcv.put(state))

        if state == State.Silenced:
            self._receivers = set()

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
        self, state: State, timeout: Optional[int | float] = None
    ) -> asyncio.Future[None]:
        """Wait for a given state to emit."""

        fut = self._loop.create_future()

        @self.listens_once(state)
        def listener() -> None:
            fut.set_result(None)

        self.events.on("state", listener)

        return asyncio.ensure_future(asyncio.wait_for(fut, timeout=timeout))

    async def subscribe(self, maxsize: int = 0) -> Receiver:
        """Subscribe to state changes."""

        rcv = Receiver(client=self, maxsize=maxsize)
        self._receivers.add(rcv)

        # TODO: What if state is silencing, waiting or ready?

        if self.state == State.Silenced:
            fut = self.wait_for(State.Ready)
            self.send(Command.Broadcast)
            await fut

        return rcv

    def receivers(self) -> List[Receiver]:
        """Currently active receivers."""

        return list(self._receivers)

    async def unsubscribe(self) -> None:
        """Unsubscribe from state changes."""

        # TODO: Should we throw if state is silenced?
        if self.state == State.Silenced:
            self._receivers = set()
            return

        # TODO: Should we throw if we're waiting for silence?
        if self.state == State.Silencing:
            return

        # TODO: Should we wait for the "ready" event before silencing?
        if self.state == State.Waiting:
            await self.wait_for(State.Ready)

        @self.listens_once(State.Silenced)
        def listener():
            self.events.emit("silenced")

        self.send(Command.Silence)


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

    await client._connection_made

    return client