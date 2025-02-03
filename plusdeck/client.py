# -*- coding: utf-8 -*-

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Callable, List, Optional, Self, Set, Tuple, Type

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

    PLAY_A = b"\x01"
    PLAY_B = b"\x02"
    FAST_FORWARD_A = b"\x03"
    FAST_FORWARD_B = b"\x04"
    PAUSE = b"\x05"
    STOP = b"\x06"
    EJECT = b"\x08"
    SUBSCRIBE = b"\x0b"
    UNSUBSCRIBE = b"\x0c"

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

    PLAYING_A = 10
    PAUSED_A = 12
    PLAYING_B = 20
    SUBSCRIBED = 21
    PAUSED_B = 22
    FAST_FORWARDING_A = 30
    FAST_FORWARDING_B = 40
    STOPPED = 50
    EJECTED = 60
    SUBSCRIBING = -1
    UNSUBSCRIBING = -2
    UNSUBSCRIBED = -3

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

Event = Tuple[Exception, None] | Tuple[None, State]


class Receiver(asyncio.Queue[Event]):
    """Receive state change events from the Plus Deck 2C PC Cassette Deck."""

    _client: "Client"
    _receiving: bool

    def __init__(self: Self, client: "Client", maxsize=0) -> None:
        super().__init__(maxsize)
        self._client = client
        self._receiving = True

    async def get_state(self: Self, timeout: Optional[float] = None) -> State:
        async with asyncio.timeout(timeout):
            exc, state = await super().get()
            if exc:
                raise exc
            else:
                assert state, "State must be defined"
                return state

    async def expect(self: Self, state: State, timeout: Optional[float] = None) -> None:
        """
        Receive state changes until the expected state.
        """

        current = await self.get_state(timeout)

        while current != state:
            current = await self.get_state(timeout)

    async def __aiter__(self: Self) -> AsyncGenerator[State, None]:
        """Iterate over state change events."""

        while True:
            if not self._receiving:
                break

            state = await self.get_state()

            yield state

            if state == State.UNSUBSCRIBED:
                self._receiving = False

    def close(self: Self) -> None:
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
        self: Self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        _loop = loop if loop else asyncio.get_running_loop()

        self.state: State = State.UNSUBSCRIBED
        self.events: AsyncIOEventEmitter = AsyncIOEventEmitter(_loop)
        self.loop: asyncio.AbstractEventLoop = _loop
        self._connection_made: asyncio.Future[None] = self.loop.create_future()
        self._closed: asyncio.Future[None] = self.loop.create_future()
        self._receivers: Set[Receiver] = set()

    def connection_made(self: Self, transport: asyncio.BaseTransport):
        if not isinstance(transport, SerialTransport):
            self._connection_made.set_exception(
                ConnectionError("Transport is not a SerialTransport")
            )
            return

        self._transport = transport
        self._connection_made.set_result(None)

    @property
    def closed(self: Self) -> asyncio.Future:
        """
        An asyncio.Future that resolves when the connection is closed. This
        may be due either to calling `client.close()` or an Exception.
        """
        return self._closed

    def close(self: Self) -> None:
        """
        Close the connection.
        """
        self._close()

    # Internal method to close the connection, potentially due to an exception.
    def _close(self: Self, exc: Optional[Exception] = None) -> None:
        if self._transport:
            self._transport.close()

        if self.closed.done():
            if exc:
                raise exc
        elif exc:
            self.closed.set_exception(exc)
        else:
            self.closed.set_result(None)

    def _error(self: Self, exc: Exception) -> None:
        receivers = self.receivers()
        if receivers:
            for rcv in receivers:
                rcv.put_nowait((exc, None))
            return

        self._close(exc)

    def send(self, command: Command) -> None:
        """
        Send a command to the Plus Deck 2C PC Cassette Deck.
        """

        if not self._transport:
            raise ConnectionError("Connection has not yet been made.")

        if command == Command.SUBSCRIBE:
            self._on_state(State.SUBSCRIBING)
        elif command == Command.UNSUBSCRIBE:
            self._on_state(State.UNSUBSCRIBING)

        self._transport.write(command.value)

    def play_a(self: Self) -> None:
        """
        Play side A.
        """

        self.send(Command.PLAY_A)

    def play_b(self: Self) -> None:
        """
        Play side B.
        """

        self.send(Command.PLAY_B)

    def fast_forward_a(self: Self) -> None:
        """
        Fast-forward side A.
        """

        self.send(Command.FAST_FORWARD_A)

    def fast_forward_b(self: Self) -> None:
        """
        Fast-forward side B.
        """

        self.send(Command.FAST_FORWARD_B)

    def rewind_a(self: Self) -> None:
        """
        Rewind side A. Equivalent to fast-forwarding side B.
        """

        self.fast_forward_b()

    def rewind_b(self: Self) -> None:
        """
        Rewind side B. Equivalent to fast-forwarding side A.
        """

        self.fast_forward_a()

    def pause(self: Self) -> None:
        """
        Pause if playing, or start playing if paused.
        """

        self.send(Command.PAUSE)

    def stop(self: Self) -> None:
        """
        Stop the tape.
        """

        self.send(Command.STOP)

    def eject(self: Self) -> None:
        """
        Eject the tape.
        """
        self.send(Command.EJECT)

    def data_received(self: Self, data) -> None:
        try:
            for state in State.from_bytes(data):
                self._on_state(state)
        except Exception as exc:
            self._error(exc)

    def _on_state(self: Self, state: State) -> None:
        previous = self.state

        # When turning off, what I've observed is that we always receive
        # exactly one pause event. I'm not entirely sure it's reliable, but
        # until it's disproven I'm treating it as such.
        #
        # If it turns out the single event is unspecified, then the logic may
        # simply be modified to handle any event. If, however, it turns out
        # there are an unspecified number of events, we will need to resort to
        # timeouts.

        if previous == State.UNSUBSCRIBING:
            if not (state == State.PAUSED_A or state == State.PAUSED_B):
                raise SubscriptionError(f"Unexpected state {state} while unsubscribing")
            state = State.UNSUBSCRIBED

        if previous == State.UNSUBSCRIBED and state != State.SUBSCRIBING:
            raise SubscriptionError(f"Unexpected state {state} while unsubscribed")

        self.state = state

        if state != previous:
            if state == State.SUBSCRIBED:
                self.events.emit("subscribed")

            self.events.emit("state", state)

            if state == State.UNSUBSCRIBED:
                self.events.emit("unsubscribed")

            for rcv in list(self._receivers):
                rcv.put_nowait((None, state))

        if state == State.UNSUBSCRIBED:
            for rcv in list(self._receivers):
                rcv.close()

    def on(self: Self, state: State, f: StateHandler) -> Handler:
        """
        Call an event handler on a given state.
        """

        return self.listens_to(state)(f)

    def listens_to(self: Self, state: State) -> Callable[[StateHandler], Handler]:
        """
        Decorate an event handler to be called on a given state.
        """

        want = state

        def decorator(f: StateHandler) -> Handler:
            def handler(state: State) -> None:
                if state == want:
                    f()

            return self.events.add_listener("state", handler)

        return decorator

    def once(self: Self, state: State, f: StateHandler) -> Handler:
        """
        Call an event handler on a given state once.
        """

        return self.listens_once(state)(f)

    def listens_once(self: Self, state: State) -> Callable[[StateHandler], Handler]:
        """
        Decorate an event handler to be called once a given state occurs.
        """

        want = state

        def decorator(f: StateHandler) -> Handler:
            def handler(state: State) -> None:
                if state == want:
                    f()
                    self.events.remove_listener("state", handler)

            return self.events.add_listener("state", handler)

        return decorator

    def wait_for(
        self: Self, state: State, timeout: Optional[float] = None
    ) -> asyncio.Future[None]:
        """
        Wait for a given state to emit. This is a low level method - client.subscribe
        and the Receiver interface will meet most use cases.
        """

        fut = self.loop.create_future()

        @self.listens_once(state)
        def listener() -> None:
            fut.set_result(None)

        return asyncio.ensure_future(asyncio.wait_for(fut, timeout=timeout))

    async def subscribe(self: Self, maxsize: int = 0) -> Receiver:
        """
        Subscribe to state changes.
        """

        rcv = Receiver(client=self, maxsize=maxsize)
        self._receivers.add(rcv)

        if self.state == State.UNSUBSCRIBED:
            # Automatically subscribe
            fut = self.wait_for(State.SUBSCRIBED)
            self.send(Command.SUBSCRIBE)
            await fut
        elif self.state == State.SUBSCRIBING:
            # Wait for in-progress subscription to complete
            await self.wait_for(State.SUBSCRIBED)
        else:
            # Must already be subscribed
            pass

        return rcv

    def receivers(self: Self) -> List[Receiver]:
        """
        Currently active receivers.
        """

        return list(self._receivers)

    async def unsubscribe(self: Self) -> None:
        """
        Unsubscribe from state changes.
        """

        # If already unsubscribing or unsubscribed, we just need to let
        # events take their course
        if self.state in {State.UNSUBSCRIBING, State.UNSUBSCRIBED}:
            return

        # Wait until subscribed in order to avoid whacky state
        if self.state == State.SUBSCRIBING:
            await self.wait_for(State.SUBSCRIBED)

        self.send(Command.UNSUBSCRIBE)

    @asynccontextmanager
    async def session(self):
        """
        Subscribe to events inside an async context manager. Automatically
        unsubscribe when done.
        """

        rcv = await self.subscribe()
        try:
            yield rcv
        finally:
            await self.unsubscribe()


async def create_connection(
    port: str,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Client:
    """
    Create a connection to the Plus Deck 2C PC Cassette Deck.
    """

    _loop = loop if loop else asyncio.get_running_loop()

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(_loop),
        port,
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
    )

    await client._connection_made

    return client


@asynccontextmanager
async def connection(
    port: str,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> AsyncGenerator[Client, None]:
    """
    Create a connection to Plus Deck 2C PC Cassette Deck, with an associated async
    context.

    This context will automatically close the connection on exit and wait for the
    connection to close.
    """

    client = await create_connection(port, loop=loop)

    yield client

    client.close()
    await client.closed
