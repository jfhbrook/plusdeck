# -*- coding: utf-8 -*-

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Callable, List, Optional, Set, Type

from pyee.asyncio import AsyncIOEventEmitter
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

"""
A client library for the Plus Deck 2C PC Cassette Deck.
"""


class PlusDeckError(Exception):
    """An error in the Plus Deck 2C PC Cassette Deck client."""

    pass


class ConnectionError(PlusDeckError):
    """A connection error."""

    pass


class StateError(PlusDeckError):
    """An error with the Plus Deck 2c PC Cassette Deck's state."""

    pass


class SubscriptionError(StateError):
    """An error involving subscribing or unsubscribing."""

    pass


class Command(Enum):
    """A command for the Plus Deck 2C PC Cassette Deck."""

    PlayA = b"\x01"
    PlayB = b"\x02"
    FastForward = b"\x03"
    Rewind = b"\x04"
    Pause = b"\x05"
    Stop = b"\x06"
    Eject = b"\x08"
    Subscribe = b"\x0b"
    Unsubscribe = b"\x0c"

    @classmethod
    def from_bytes(cls: Type["Command"], buffer: bytes) -> List["Command"]:
        return [Command(code.to_bytes(length=1, byteorder="little")) for code in buffer]

    @classmethod
    def from_byte(cls: Type["Command"], buffer: bytes) -> "Command":
        if len(buffer) != 1:
            raise ValueError("Can not convert multiple bytes into a single Command")
        return cls.from_bytes(buffer)[0]

    def to_bytes(self: "Command") -> bytes:
        return self.value


class State(Enum):
    """The state of the Plus Deck 2C PC Cassette Deck."""

    PlayingA = 0x0A
    PausedA = 0x0C
    PlayingB = 0x14
    Subscribed = 0x15
    PausedB = 0x16
    FastForwarding = 0x1E
    Rewinding = 0x28
    Stopped = 0x32
    Ejected = 0x3C
    Subscribing = -1
    Unsubscribing = -2
    Unsubscribed = -3

    @classmethod
    def from_bytes(cls: Type["State"], buffer: bytes) -> List["State"]:
        return [cls(code) for code in buffer]

    @classmethod
    def from_byte(cls: Type["State"], buffer: bytes) -> "State":
        if len(buffer) != 1:
            raise ValueError("Can not convert multiple bytes to a single State")
        return cls.from_bytes(buffer)[0]

    def to_bytes(self: "State") -> bytes:
        if self.value < 0:
            raise ValueError(f"Can not convert {self} to bytes")
        return self.value.to_bytes()


Handler = Callable[[State], None]
StateHandler = Callable[[], None]


class Receiver(asyncio.Queue):
    """Receive state change events from the Plus Deck 2C PC Cassette Deck."""

    _client: "Client"
    _receiving: bool

    def __init__(self, client: "Client", maxsize=0):
        super().__init__(maxsize)
        self._client = client
        self._receiving = True

    async def expect(self, state: State) -> None:
        """Receive state changes until the expected state."""
        current = await self.get()

        while current != state:
            current = await self.get()

    async def __aiter__(self) -> AsyncGenerator[State, None]:
        """Iterate over state change events."""

        while True:
            if not self._receiving:
                break

            state = await self.get()

            yield state

            if state == State.Unsubscribed:
                self._receiving = False

    def close(self) -> None:
        """Close the receiver."""

        self._receiving = False
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

        self.state: State = State.Unsubscribed
        self.events: AsyncIOEventEmitter = AsyncIOEventEmitter(_loop)
        self._loop: asyncio.AbstractEventLoop = _loop
        self._connection_made: asyncio.Future[None] = self._loop.create_future()
        self._receivers: Set[Receiver] = set()

    def connection_made(self, transport: asyncio.BaseTransport):
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._connection_made.set_result(None)



    def close(self) -> None:
        if not self._transport:
            raise ConnectionError("Can not close uninitialized connection")
        self._transport.close()

    def send(self, command: Command):
        """Send a command to the Plus Deck 2C."""

        if not self._transport:
            raise ConnectionError("Connection has not yet been made.")

        if command == Command.Subscribe:
            self._on_state(State.Subscribing)
        elif command == Command.Unsubscribe:
            self._on_state(State.Unsubscribing)

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

        if previous == State.Unsubscribing:
            if not (state == State.PausedA or state == State.PausedB):
                raise SubscriptionError(f"Unexpected state {state} while unsubscribing")
            state = State.Unsubscribed

        if previous == State.Unsubscribed and state != State.Subscribing:
            raise SubscriptionError(f"Unexpected state {state} while unsubscribed")

        self.state = state

        if state != previous:
            if state == State.Subscribed:
                self.events.emit("subscribed")

            self.events.emit("state", state)

            if state == State.Unsubscribed:
                self.events.emit("unsubscribed")

            for rcv in list(self._receivers):
                self._loop.create_task(rcv.put(state))

        if state == State.Unsubscribed:
            for rcv in list(self._receivers):
                rcv.close()

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

        if self.state == State.Unsubscribed:
            # Automatically subscribe
            fut = self.wait_for(State.Subscribed)
            self.send(Command.Subscribe)
            await fut
        elif self.state == State.Subscribing:
            # Wait for in-progress subscription to complete
            await self.wait_for(State.Subscribed)
        else:
            # Must already be subscribed
            pass

        return rcv

    def receivers(self) -> List[Receiver]:
        """Currently active receivers."""

        return list(self._receivers)

    async def unsubscribe(self) -> None:
        """Unsubscribe from state changes."""

        # If already unsubscribing or unsubscribed, we just need to let
        # events take their course
        if self.state in {State.Unsubscribing, State.Unsubscribed}:
            return

        # Wait until subscribed in order to avoid whacky state
        if self.state == State.Subscribing:
            await self.wait_for(State.Subscribed)

        self.send(Command.Unsubscribe)

    @asynccontextmanager
    async def session(self):
        rcv = await self.subscribe()
        try:
            yield rcv
        finally:
            await self.unsubscribe()


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
