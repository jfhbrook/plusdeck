# -*- coding: utf-8 -*-

import asyncio
from typing import cast, List, Optional
from unittest.mock import call, Mock

import pytest
from serial_asyncio import SerialTransport

from plusdeck.client import Client, Command, State, SubscriptionError

TEST_TIMEOUT = 0.01


@pytest.mark.asyncio
async def test_online(client: Client) -> None:
    """Comes online when the connection is made."""

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
    [(command, command.to_bytes()) for command in Command],
)
@pytest.mark.asyncio
async def test_command(client: Client, command: Command, code: bytes) -> None:
    """Sends Commands to the transport."""
    client.send(command)
    assert client._transport is not None
    cast(Mock, client._transport.write).assert_called_with(code)


@pytest.mark.parametrize(
    "state,data",
    [
        (state, state.to_bytes())
        for state in State
        if state
        not in {
            State.SUBSCRIBING,
            State.SUBSCRIBED,
            State.UNSUBSCRIBING,
            State.UNSUBSCRIBED,
        }
    ],
)
@pytest.mark.asyncio
async def test_state_events(client: Client, state: State, data: bytes) -> None:
    """Emits the state event."""

    client.state = State.SUBSCRIBED

    received: Optional[State] = None

    def handler(state: State) -> None:
        nonlocal received
        received = state

    client.events.on("state", handler)

    client.data_received(data + data)

    assert received and received == state


@pytest.mark.asyncio
async def test_subscription_events(client: Client) -> None:
    """Emits subscription events."""

    # Expecting a subscribed state
    client.state = State.SUBSCRIBING

    handler = Mock(name="handler")
    subscribed_handler = Mock(name="subscribe_handler")
    unsubscribed_handler = Mock(name="unsubscribe_handler")

    client.events.on("subscribed", handler)
    client.events.on("subscribed", subscribed_handler)
    client.events.on("state", handler)
    client.events.on("unsubscribed", handler)
    client.events.on("unsubscribed", unsubscribed_handler)

    # Receive subscribed state
    client.data_received(b"\x15")

    assert client.state == State.SUBSCRIBED

    # Receive playing state
    client.data_received(b"\x0a")

    assert client.state == State.PLAYING_A

    # Expect a pause state to signal unsubscribed
    client.send(Command.UNSUBSCRIBE)

    assert client.state == State.UNSUBSCRIBING

    # Receive pause state
    client.data_received(b"\x0c")

    assert client.state == State.UNSUBSCRIBED

    # Did our events fire in order?
    handler.assert_has_calls(
        [
            # Subscribe
            call(),
            call(State.SUBSCRIBED),
            call(State.PLAYING_A),
            call(State.UNSUBSCRIBING),
            call(State.UNSUBSCRIBED),
            # Unsubscribe
            call(),
        ]
    )

    # Did the right events fire?
    subscribed_handler.assert_called_once()
    unsubscribed_handler.assert_called_once()


@pytest.mark.asyncio
async def test_listens_to(client: Client) -> None:
    """Listens for state."""

    call_count = 0

    @client.listens_to(State.PLAYING_A)
    def handler() -> None:
        nonlocal call_count
        call_count += 1

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.STOPPED

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0c")

    assert call_count == 1
    assert client.state == State.PAUSED_A


@pytest.mark.asyncio
async def test_on(client: Client) -> None:
    """Calls handler on state."""

    call_count = 0

    def handler() -> None:
        nonlocal call_count
        call_count += 1

    client.on(State.PLAYING_A, handler)

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.STOPPED

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0c")

    assert call_count == 1
    assert client.state == State.PAUSED_A


@pytest.mark.asyncio
async def test_listens_once(client: Client) -> None:
    """Listens for state once."""

    call_count = 0

    @client.listens_once(State.PLAYING_A)
    def handler() -> None:
        nonlocal call_count
        call_count += 1

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.STOPPED

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0c")

    assert call_count == 1
    assert client.state == State.PAUSED_A


@pytest.mark.asyncio
async def test_once(client: Client) -> None:
    """Calls handler once."""
    call_count = 0

    def handler() -> None:
        nonlocal call_count
        call_count += 1

    client.once(State.PLAYING_A, handler)

    client.data_received(b"\x15\x32")

    assert call_count == 0
    assert client.state == State.STOPPED

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0a")

    assert call_count == 1
    assert client.state == State.PLAYING_A

    client.data_received(b"\x0c")

    assert call_count == 1
    assert client.state == State.PAUSED_A


@pytest.mark.parametrize(
    "state",
    [
        state
        for state in State
        if state
        not in {
            State.SUBSCRIBING,
            State.SUBSCRIBED,
            State.UNSUBSCRIBING,
            State.UNSUBSCRIBED,
        }
    ],
)
@pytest.mark.asyncio
async def test_wait_for(client: Client, state: State) -> None:
    """Waits for a given state."""

    fut = client.wait_for(state, timeout=TEST_TIMEOUT)

    client.data_received(state.to_bytes())

    await fut


@pytest.mark.asyncio
async def test_subscribe_when_unsubscribed(client: Client) -> None:
    """Waits for subscribed event when subscribing."""

    # Ensure starting state is unsubscribed
    client.state = State.UNSUBSCRIBED

    # When transport write is called, simulate receiving State.SUBSCRIBED
    def emit_ready(_) -> None:
        client.data_received(b"\x15")

    assert client._transport is not None
    cast(Mock, client._transport.write).side_effect = emit_ready

    # Giddyup
    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    # Sent the "subscribe" command
    cast(Mock, client._transport.write).assert_called_with(b"\x0b")

    # Set the current state
    assert client.state == State.SUBSCRIBED


@pytest.mark.parametrize("state", [State.EJECTED, State.SUBSCRIBED])
@pytest.mark.asyncio
async def test_subscribe_when_subscribed(client: Client, state: State) -> None:
    """Creates receiver when already subscribed."""

    client.state = state

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())
    assert client._transport is not None
    cast(Mock, client._transport.write).assert_not_called()
    assert client.state == state


@pytest.mark.parametrize(
    "buffer,state",
    [
        (state.to_bytes(), state)
        for state in State
        if state
        not in {
            State.EJECTED,
            State.SUBSCRIBING,
            State.UNSUBSCRIBING,
            State.UNSUBSCRIBED,
        }
    ],
)
@pytest.mark.asyncio
async def test_receive_state(client: Client, buffer, state) -> None:
    """Receives a state."""

    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut = asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)

    client.data_received(buffer)

    assert (await fut) == state


@pytest.mark.parametrize(
    "buffer,state",
    [
        (state.to_bytes(), state)
        for state in State
        if state
        not in {
            State.EJECTED,
            State.SUBSCRIBING,
            State.UNSUBSCRIBING,
            State.UNSUBSCRIBED,
        }
    ],
)
@pytest.mark.asyncio
async def test_expect_state(client: Client, buffer, state) -> None:
    """Expect a state."""

    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut = asyncio.wait_for(rcv.expect(state), timeout=TEST_TIMEOUT)

    client.data_received(buffer)

    await fut


@pytest.mark.asyncio
async def test_expect_timeout(client: Client) -> None:
    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    with pytest.raises(TimeoutError):
        await rcv.expect(State.EJECTED, timeout=0.1)


@pytest.mark.asyncio
async def test_receive_duplicate_state(client: Client) -> None:
    """Receives a state once."""
    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut = asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)

    client.data_received(b"\x32")

    assert (await fut) == State.STOPPED
    assert client.state == State.STOPPED

    fut2 = asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)

    client.data_received(b"\x32")

    with pytest.raises(asyncio.TimeoutError):
        await fut2

    assert client.state == State.STOPPED


@pytest.mark.asyncio
async def test_many_receivers(client: Client) -> None:
    """Juggles many receivers."""

    client.state = State.UNSUBSCRIBED

    def emit_ready(_) -> None:
        client.data_received(b"\x15")

    assert client._transport is not None
    cast(Mock, client._transport.write).side_effect = emit_ready

    ready = client.wait_for(State.SUBSCRIBED, timeout=TEST_TIMEOUT)

    # Create first receiver before subscribing
    rcv1 = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv1 in set(client.receivers())

    # Wait until listening
    await ready

    cast(Mock, client._transport.write).assert_called_once_with(b"\x0b")

    # Create second receiver after subscribing
    rcv2 = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv1 in set(client.receivers())
    assert rcv2 in set(client.receivers())

    ejected = client.wait_for(State.EJECTED, timeout=TEST_TIMEOUT)
    client.data_received(b"\x3c")
    await ejected

    # Should have three states from first receiver
    state1a = await asyncio.wait_for(rcv1.get_state(), timeout=TEST_TIMEOUT)
    state1b = await asyncio.wait_for(rcv1.get_state(), timeout=TEST_TIMEOUT)
    state1c = await asyncio.wait_for(rcv1.get_state(), timeout=TEST_TIMEOUT)

    assert [state1a, state1b, state1c] == [
        State.SUBSCRIBING,
        State.SUBSCRIBED,
        State.EJECTED,
    ]

    # Should have one state from second receiver
    state2 = await asyncio.wait_for(rcv2.get_state(), timeout=TEST_TIMEOUT)

    assert state2 == State.EJECTED


@pytest.mark.asyncio
async def test_close_receiver(client: Client) -> None:
    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    rcv.close()

    assert len(client.receivers()) == 0


@pytest.mark.parametrize(
    "buffer", [state.to_bytes() for state in {State.PAUSED_A, State.PAUSED_B}]
)
@pytest.mark.asyncio
async def test_unsubscribe(client: Client, buffer) -> None:
    """Unsubscribe a subscribed client."""

    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    fut_wait_for = client.wait_for(State.UNSUBSCRIBED, timeout=TEST_TIMEOUT)
    fut_get1 = asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)
    fut_get2 = asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)

    client.send(Command.UNSUBSCRIBE)
    client.data_received(buffer)

    assert len(client.receivers()) == 0

    await fut_wait_for
    assert (await fut_get1) == State.UNSUBSCRIBING
    assert (await fut_get2) == State.UNSUBSCRIBED

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)


@pytest.mark.parametrize(
    "state",
    [
        state
        for state in State
        if state
        not in {
            State.PAUSED_A,
            State.PAUSED_B,
            State.SUBSCRIBING,
            State.UNSUBSCRIBING,
            State.UNSUBSCRIBED,
        }
    ],
)
@pytest.mark.asyncio
async def test_failed_unsubscribe(client: Client, state: State) -> None:
    """Raises an error if client fails to unsubscribe."""

    client.state = State.UNSUBSCRIBING

    client.data_received(state.to_bytes())

    with pytest.raises(SubscriptionError):
        await client.closed


@pytest.mark.parametrize("state", [State.UNSUBSCRIBING, State.UNSUBSCRIBED])
@pytest.mark.asyncio
async def test_unsubscribe_when_unsubscribed(client: Client, state: State) -> None:
    """Unsubscribes when already unsubscribed."""

    client.state = state

    await client.unsubscribe()


@pytest.mark.asyncio
async def test_unsubscribe_when_unsubscribing(client: Client) -> None:
    """Unsubscribes when already unsubscribing."""

    client.state = State.SUBSCRIBING

    fut = client.unsubscribe()

    # Send subscribing event
    client.data_received(b"\x15")

    await fut

    assert client._transport is not None
    cast(Mock, client._transport.write).assert_called_with(b"\x0c")


@pytest.mark.parametrize(
    "buffer", [state.to_bytes() for state in {State.PAUSED_A, State.PAUSED_B}]
)
@pytest.mark.asyncio
async def test_iter_receiver(client: Client, buffer: bytes) -> None:
    """Iterates a receiver."""

    client.state = State.EJECTED

    rcv = await asyncio.wait_for(client.subscribe(), timeout=TEST_TIMEOUT)

    assert rcv in set(client.receivers())

    # Receive some events
    client.data_received(b"\x32")
    client.data_received(b"\x0a")

    # Close the connection
    client.send(Command.UNSUBSCRIBE)
    client.data_received(buffer)

    states = [State.UNSUBSCRIBED, State.UNSUBSCRIBING, State.PLAYING_A, State.STOPPED]

    async def iterate() -> None:
        async for state in rcv:
            assert state == states.pop()

        assert len(client.receivers()) == 0

    fut = asyncio.wait_for(iterate(), timeout=TEST_TIMEOUT)

    await fut


@pytest.mark.asyncio
async def test_session_queue(client: Client) -> None:
    client.state = State.UNSUBSCRIBED

    received = [State.PAUSED_A, State.PLAYING_A, State.SUBSCRIBED]

    # When transport write is called, simulate receiving State.SUBSCRIBED
    def emit_data(_) -> None:
        client.data_received(received.pop().to_bytes())

    assert client._transport is not None
    cast(Mock, client._transport.write).side_effect = emit_data

    state1: Optional[State] = None
    state2: Optional[State] = None
    state3: Optional[State] = None

    unsubbed = client.wait_for(State.UNSUBSCRIBED)

    async with client.session() as rcv:
        client.send(Command.PLAY_A)

        state1 = await asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)
        state2 = await asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)
        state3 = await asyncio.wait_for(rcv.get_state(), timeout=TEST_TIMEOUT)

    await asyncio.wait_for(unsubbed, timeout=TEST_TIMEOUT)

    cast(Mock, client._transport.write).assert_has_calls(
        [
            call(Command.SUBSCRIBE.to_bytes()),
            call(Command.PLAY_A.to_bytes()),
            call(Command.UNSUBSCRIBE.to_bytes()),
        ]
    )

    assert [state1, state2, state3] == [
        State.SUBSCRIBING,
        State.SUBSCRIBED,
        State.PLAYING_A,
    ]


@pytest.mark.asyncio
async def test_session_iterator(client: Client) -> None:
    client.state = State.UNSUBSCRIBED

    received = [State.PAUSED_A, State.PLAYING_A, State.SUBSCRIBED]

    # When transport write is called, simulate receiving State.SUBSCRIBED
    def emit_data(_) -> None:
        client.data_received(received.pop().to_bytes())

    assert client._transport is not None
    cast(Mock, client._transport.write).side_effect = emit_data

    states: List[State] = []

    unsubbed = client.wait_for(State.UNSUBSCRIBED)

    async with client.session() as rcv:
        client.send(Command.PLAY_A)

        async for state in rcv:
            states.append(state)
            if len(states) == 3:
                rcv.close()

    await asyncio.wait_for(unsubbed, timeout=TEST_TIMEOUT)

    cast(Mock, client._transport.write).assert_has_calls(
        [
            call(Command.SUBSCRIBE.to_bytes()),
            call(Command.PLAY_A.to_bytes()),
            call(Command.UNSUBSCRIBE.to_bytes()),
        ]
    )

    assert states == [
        State.SUBSCRIBING,
        State.SUBSCRIBED,
        State.PLAYING_A,
    ]
