# -*- coding: utf-8 -*-

import asyncio
from typing import Optional

import pytest

from plusdeck import Command, State


@pytest.mark.asyncio
async def test_online(client):
    """The client comes online when the connection is made."""

    client.connection_made(client._transport)

    await asyncio.wait_for(client._online, timeout=1)


@pytest.mark.parametrize(
    "command,code",
    [(Command.PlaySideA, b"\x01"), (Command.Close, b"\x0c")],
)
@pytest.mark.asyncio
@pytest.mark.skip
async def test_command(client, command, code):
    """Commands are sent to the transport."""
    client.send(command)
    client._transport.write.assert_called_with(code)


@pytest.mark.parametrize("state", [state.value.to_bytes() for state in State])
@pytest.mark.asyncio
@pytest.mark.skip
async def test_events(client, state):
    """Events are emitted."""

    received: Optional[State] = None

    def handler(state: State):
        received = state

    client.events.on("state", handler)

    client.data_received(state + state)

    assert received and received.value == state


@pytest.mark.skip
@pytest.mark.asyncio
async def test_listens_to(client):
    """Listens for state."""
    pass


@pytest.mark.skip
def tests_on(client):
    """Calls handler on state."""
    pass


@pytest.mark.skip
def test_listens_once(client):
    """Listens for state once."""
    pass


@pytest.mark.skip
def test_once(client):
    """Calls handler once."""
    pass


@pytest.mark.parametrize("state", [state for state in State])
@pytest.mark.asyncio
@pytest.mark.skip
async def test_wait_for(client, state):
    """Waits for a given state."""

    fut = client.wait_for(state, timeout=1)

    client.data_received(state.value.to_bytes())

    await fut


@pytest.mark.asyncio
@pytest.mark.skip
async def test_listen_when_closed(client):
    """Waits for ready event when starting to listen."""

    # Ensure starting state is closed
    client.state = State.Closed

    # Mock the Plus Deck sending the "ready" event after receiving the
    # "listen" command
    def emit_ready(_data):
        client.data_received(b"\x15")

    client._transport.write.side_effect = emit_ready

    # Giddyup
    await asyncio.wait_for(client.listen(), timeout=1)

    # Sent the "listen" command
    client._receiver.write.assert_called_with(b"\x0b")

    # Set the current state
    assert client.state == State.Ready


@pytest.mark.asyncio
@pytest.mark.skip
async def test_listen_when_listening(client):
    """Creates receiver when already listening."""

    client.state = State.Ejected

    await asyncio.wait_for(client.listen(), timeout=1)

    client._transport.assert_not_called()
    assert client.state == State.Ejected


@pytest.mark.skip
def test_receive_state(client):
    """Receives a state."""


@pytest.mark.skip
def test_many_receivers(client):
    """Juggles many receivers."""


@pytest.mark.skip
def test_close(client):
    """Closes a listening client."""


@pytest.mark.skip
def test_attempted_close(client):
    """Throws an error if client fails to close."""


@pytest.mark.skip
def test_close_when_closed(client):
    """Closes when already closed."""


@pytest.mark.skip
def test_iter_receiver(client):
    """Iterates a receiver."""
