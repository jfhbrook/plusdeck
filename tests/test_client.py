# -*- coding: utf-8 -*-

import asyncio
from typing import Optional
from unittest.mock import Mock

import pytest
from serial_asyncio import SerialTransport

from plusdeck import Command, State

TEST_TIMEOUT = 0.01


@pytest.mark.asyncio
async def test_online(client):
    """The client comes online when the connection is made."""

    client.connection_made(
        SerialTransport(
            loop=asyncio.get_running_loop(),
            protocol=client,
            serial_instance=Mock(name="SerialInstance"),
        )
    )

    await asyncio.wait_for(client._connection_made, timeout=TEST_TIMEOUT)


@pytest.mark.parametrize(
    "command,code",
    [(Command.PlaySideA, b"\x01"), (Command.Close, b"\x0c")],
)
@pytest.mark.asyncio
async def test_command(client, command, code):
    """Commands are sent to the transport."""
    client.send(command)
    client._transport.write.assert_called_with(code)


@pytest.mark.parametrize("state", [state.value.to_bytes() for state in State])
@pytest.mark.asyncio
async def test_events(client, state):
    """Events are emitted."""

    received: Optional[State] = None

    def handler(state: State):
        nonlocal received
        received = state

    client.events.on("state", handler)

    client.data_received(state + state)

    assert received and received.value == int.from_bytes(state, byteorder="little")


@pytest.mark.asyncio
async def test_listens_to(client):
    """Listens for state."""

    call_count = 0

    @client.listens_to(State.PlayingA)
    def handler():
        nonlocal call_count
        call_count += 1

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.Stopped

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x16")

    assert call_count == 1
    assert client.state == State.PausedOnA


@pytest.mark.asyncio
async def tests_on(client):
    """Calls handler on state."""

    call_count = 0

    def handler():
        nonlocal call_count
        call_count += 1

    client.on(State.PlayingA, handler)

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.Stopped

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x16")

    assert call_count == 1
    assert client.state == State.PausedOnA


@pytest.mark.asyncio
async def test_listens_once(client):
    """Listens for state once."""

    call_count = 0

    @client.listens_once(State.PlayingA)
    def handler():
        nonlocal call_count
        call_count += 1

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.Stopped

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x16")

    assert call_count == 1
    assert client.state == State.PausedOnA


@pytest.mark.asyncio
async def test_once(client):
    """Calls handler once."""
    call_count = 0

    def handler():
        nonlocal call_count
        call_count += 1

    client.once(State.PlayingA, handler)

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.Stopped

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PlayingA

    client.data_received(b"\x16")

    assert call_count == 1
    assert client.state == State.PausedOnA


@pytest.mark.parametrize("state", [state for state in State])
@pytest.mark.asyncio
async def test_wait_for(client, state):
    """Waits for a given state."""

    fut = client.wait_for(state, timeout=TEST_TIMEOUT)

    client.data_received(state.value.to_bytes())

    await fut


@pytest.mark.asyncio
async def test_listen_when_closed(client):
    """Waits for ready event when starting to listen."""

    # Ensure starting state is closed
    client.state = State.Closed

    # When transport write is called, simulate receiving State.Ready
    def emit_ready(_):
        client.data_received(b"\x15")

    client._transport.write.side_effect = emit_ready

    # Giddyup
    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    # Sent the "listen" command
    client._transport.write.assert_called_with(b"\x0b")

    # Set the current state
    assert client.state == State.Ready


@pytest.mark.asyncio
async def test_listen_when_listening(client):
    """Creates receiver when already listening."""

    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())
    client._transport.assert_not_called()
    assert client.state == State.Ejected


@pytest.mark.parametrize(
    "buffer,state",
    [
        (state.value.to_bytes(), state)
        for state in State
        if state != State.Closed and state != State.Ejected
    ],
)
@pytest.mark.asyncio
async def test_receive_state(client, buffer, state):
    """Receives a state."""

    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut = asyncio.wait_for(rcv.get(), timeout=TEST_TIMEOUT)

    client.data_received(buffer)

    assert (await fut) == state


@pytest.mark.asyncio
async def test_receive_duplicate_state(client):
    """Receives a state once."""
    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut = asyncio.wait_for(rcv.get(), timeout=TEST_TIMEOUT)

    client.data_received(b"\x32")

    assert (await fut) == State.Stopped
    assert client.state == State.Stopped

    fut2 = asyncio.wait_for(rcv.get(), timeout=TEST_TIMEOUT)

    client.data_received(b"\x32")

    with pytest.raises(asyncio.TimeoutError):
        await fut2

    assert client.state == State.Stopped


@pytest.mark.asyncio
async def test_many_receivers(client):
    """Juggles many receivers."""

    client.state = State.Closed

    def emit_ready(_):
        client.data_received(b"\x15")

    client._transport.write.side_effect = emit_ready

    ready = client.wait_for(State.Ready, timeout=TEST_TIMEOUT)

    # Create first receiver before listening
    rcv1 = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv1 in set(client.receivers())

    # Wait until listening
    await ready

    # Create second receiver after listening
    rcv2 = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv1 in set(client.receivers())
    assert rcv2 in set(client.receivers())

    ejected = client.wait_for(State.Ejected, timeout=TEST_TIMEOUT)
    client.data_received(b"\x3c")
    await ejected

    # Should have two states from first receiver
    state1a = await asyncio.wait_for(rcv1.get(), timeout=TEST_TIMEOUT)
    state1b = await asyncio.wait_for(rcv1.get(), timeout=TEST_TIMEOUT)

    assert state1a == State.Ready
    assert state1b == State.Ejected

    # Should have one state from second receiver
    state2 = await asyncio.wait_for(rcv2.get(), timeout=TEST_TIMEOUT)

    assert state2 == State.Ejected


@pytest.mark.asyncio
async def test_remove_receiver(client):
    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    rcv.remove()

    assert len(list(client.receivers())) == 0


@pytest.mark.parametrize(
    "buffer", [State.PausedOnA.value.to_bytes(), State.PausedOnB.value.to_bytes()]
)
@pytest.mark.asyncio
async def test_close(client, buffer):
    """Closes a listening client."""

    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut_wait_for = client.wait_for(State.Closed, timeout=TEST_TIMEOUT)
    fut_get = asyncio.wait_for(rcv.get(), timeout=TEST_TIMEOUT)

    client.send(Command.Close)
    client.data_received(buffer)

    assert len(list(client.receivers())) == 0

    await fut_wait_for
    assert (await fut_get) == State.Closed

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(rcv.get(), timeout=TEST_TIMEOUT)


@pytest.mark.skip
def test_attempted_close(client):
    """Throws an error if client fails to close."""


@pytest.mark.parametrize(
    "buffer", [State.PausedOnA.value.to_bytes(), State.PausedOnB.value.to_bytes()]
)
@pytest.mark.asyncio
@pytest.mark.skip
async def test_close_when_closed(client, buffer):
    """Closes when already closed."""

    pass


@pytest.mark.parametrize(
    "buffer", [State.PausedOnA.value.to_bytes(), State.PausedOnB.value.to_bytes()]
)
@pytest.mark.asyncio
async def test_iter_receiver(client, buffer):
    """Iterates a receiver."""

    client.state = State.Ejected

    rcv = await asyncio.wait_for(client.listen(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    # Receive some events
    client.data_received(b"\x32")
    client.data_received(b"\x0a")

    # Close the connection
    client.send(Command.Close)
    client.data_received(buffer)

    states = [State.PlayingA, State.Stopped]

    async def iterate():
        async for state in rcv:
            assert state == states.pop()

        assert len(list(client.receivers())) == 0

    fut = asyncio.wait_for(iterate(), timeout=TEST_TIMEOUT)

    await fut
