# -*- coding: utf-8 -*-

import asyncio
from enum import Enum
from typing import Any, cast, Dict, Optional, Tuple, Type

from serial_asyncio import create_serial_connection, SerialTransport

"""
A client library for the Plus Deck 2C PC Cassette Drive.
"""

# TODO: Make sure the Plus Deck works reliably at this baud rate.
# See: https://github.com/pyserial/pyserial/blob/7aeea35429d15f3eefed10bbb659674638903e3a/serial/rfc2217.py#L381  # noqa
BAUD_RATE = 115200


class Command(Enum):
    """A Plus Deck 2C command."""

    PlaySideA = b"\x01"
    PlaySideB = b"\x02"
    FastForward = b"\x03"
    Rewind = b"\x04"
    TogglePause = b"\x05"
    Stop = b"\x06"
    Eject = b"\x08"
    # TODO: I don't like these command names.
    On = b"\x0b"
    Off = b"\x0c"


class State(Enum):
    """A Plus Deck 2C state."""

    PlayingA = 0x0A
    PausedOnB = 0x0C
    PlayingB = 0x14
    Ready = 0x15
    PausedOnA = 0x16
    FastForwarding = 0x1E
    Rewinding = 0x28
    Stopped = 0x32
    Ejected = 0x3C
    Off = 0x00


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


class PlusDeckProtocol(asyncio.Protocol):
    """An asyncio Protocol for the Plus Deck 2C PC Cassette Drive."""

    state: State
    _transport: SerialTransport | None
    _sent_off: bool

    def __init__(self):
        self._sent_off = False
        self.state = State.Off

    def connection_made(self, transport: asyncio.BaseTransport):
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport

    def send_command(self, command: Command):
        """Send a command to the Plus Deck 2C."""

        if not self._transport:
            raise ConnectionError("Connection has not yet been made.")

        self._transport.write(command.value)

        if command == Command.Off:
            self._sent_off = True
        else:
            self._sent_off = False

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

        sent_off = self._sent_off
        self._sent_off = False

        if sent_off and (state == State.PausedOnA or state == State.PausedOnB):
            state = State.Off

        self.state = state

        # Emit a "ready" event immediately.
        #
        # What I've observed is that we get exactly one "ready" event.
        # However, I still debounce the event just in case.
        if state == State.Ready and previous != State.Ready:
            self.on_ready()

        # Emit the state no matter what it is
        self.on_state(state)

        # We only emit on state *changes*, excepting for when we thought
        # state was off.
        if (state == previous and state != State.Off) or state == State.Ready:
            return

        if state == State.PlayingA:
            self.on_play(Side.A)
        elif state == State.PausedOnB:
            self.on_pause(Side.B)
        elif state == State.PlayingB:
            self.on_play(Side.B)
        elif state == State.PausedOnA:
            self.on_pause(Side.A)
        elif state == State.FastForwarding:
            self.on_fast_forward()
        elif state == State.Rewinding:
            self.on_rewind()
        elif state == State.Stopped:
            self.on_stop()
        elif state == State.Ejected:
            self.on_eject()
        elif state == State.Off:
            self.on_off()
        else:
            # Should be unreachable.
            code = state.value
            raise StateError(f"Unhandled state: {code}", code)

    def on_state(self, state: State):
        """The Plus Deck has emitted its state."""
        pass

    def on_ready(self):
        """The Plus Deck is ready."""
        pass

    def on_play(self, side: Side):
        """The Plus Deck has started playing."""
        pass

    def on_pause(self, side: Side):
        """The Plus Deck has been paused."""
        pass

    def on_stop(self):
        """The Plus Deck has stopped."""
        pass

    def on_fast_forward(self):
        """The Plus Deck is fast-forwarding."""
        pass

    def on_rewind(self):
        """The Plus Deck is rewinding."""
        pass

    def on_eject(self):
        """The Plus Deck has ejected."""
        pass

    def on_off(self):
        """The Plus Deck has been turned off."""
        pass


async def create_connection(
    url: str,
    protocol: Type[PlusDeckProtocol],
    *args: Tuple[Any, ...],
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baudrate: int = BAUD_RATE,
    **kwargs: Dict[str, Any],
) -> Tuple[SerialTransport, PlusDeckProtocol]:
    _loop = loop if loop else asyncio.get_running_loop()
    kwargs["baudrate"] = cast(Any, baudrate)

    return await create_serial_connection(_loop, protocol, url, *args, **kwargs)
