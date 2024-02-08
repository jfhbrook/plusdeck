# -*- coding: utf-8 -*-

from unittest.mock import call

import pytest

from plusdeck_client import Command, Side, State


@pytest.mark.parametrize(
    "command,code,sent_off",
    [(Command.PlaySideA, b"\x01", False), (Command.Off, b"\x0c", True)],
)
def test_command(protocol, command, code, sent_off):
    """Test sending a command"""
    protocol.send_command(command)
    protocol._transport.write.assert_called_with(code)
    assert protocol._sent_off == sent_off


def test_ready(protocol, event_methods):
    """Test for 'ready' event"""

    event_methods.remove("on_ready")

    protocol.data_received(b"\x15\x15")
    protocol.on_state.assert_has_calls([call(State.Ready), call(State.Ready)])
    protocol.on_ready.assert_called_once_with()

    for method in event_methods:
        getattr(protocol, method).assert_not_called()


@pytest.mark.parametrize(
    "code,state,method,side",
    [
        (b"\x0a", State.PlayingA, "on_play", Side.A),
        (b"\x0c", State.PausedOnB, "on_pause", Side.B),
        (b"\x14", State.PlayingB, "on_play", Side.B),
        (b"\x16", State.PausedOnA, "on_pause", Side.A),
    ],
)
def test_sided_event(protocol, event_methods, code, state, method, side):
    """Tests for events which have a side"""

    event_methods.remove(method)

    protocol.data_received(code + code)
    protocol.on_state.assert_has_calls([call(state), call(state)])
    getattr(protocol, method).assert_called_once_with(side)

    for method in event_methods:
        getattr(protocol, method).assert_not_called()


@pytest.mark.parametrize(
    "code,state,method",
    [
        (b"\x1e", State.FastForwarding, "on_fast_forward"),
        (b"\x28", State.Rewinding, "on_rewind"),
        (b"\x32", State.Stopped, "on_stop"),
        (b"\x3c", State.Ejected, "on_eject"),
    ],
)
def test_unsided_event(protocol, event_methods, code, state, method):
    """Tests for events which don't have a side"""
    event_methods.remove(method)

    protocol.data_received(code + code)
    protocol.on_state.assert_has_calls([call(state), call(state)])
    getattr(protocol, method).assert_called_once_with()

    for method in event_methods:
        getattr(protocol, method).assert_not_called()


@pytest.mark.parametrize("code", [b"\x0c", b"\x16"])
def test_off(protocol, event_methods, code):
    """Test that the off event fires under normal circumstances"""
    event_methods.remove("on_off")

    protocol.state = State.Ejected

    protocol.send_command(Command.Off)
    protocol.data_received(code)
    protocol.on_state.assert_called_once_with(State.Off)
    protocol.on_off.assert_called_once_with()

    for method in event_methods:
        getattr(protocol, method).assert_not_called()


@pytest.mark.parametrize(
    "code,state,method",
    [
        (b"\x1e", State.FastForwarding, "on_fast_forward"),
        (b"\x15", State.Ready, "on_ready"),
    ],
)
def test_off_but_not(protocol, event_methods, code, state, method):
    """
    Test that the off event does not fire when we receive a non-exiting code,
    such as playing
    """
    event_methods.remove(method)

    protocol.state = State.Ejected

    protocol.send_command(Command.Off)
    protocol.data_received(code)
    protocol.on_state.assert_called_once_with(state)
    getattr(protocol, method).assert_called_once_with()

    for method in event_methods:
        getattr(protocol, method).assert_not_called()


@pytest.mark.parametrize("code", [b"\x0c", b"\x16"])
def test_off_when_off(protocol, event_methods, code):
    """
    Test that the off event fires even when the Plus Deck was thought to
    already be off
    """
    event_methods.remove("on_off")

    protocol.send_command(Command.Off)
    protocol.data_received(code)
    protocol.on_state.assert_called_once_with(State.Off)
    protocol.on_off.assert_called_once_with()

    for method in event_methods:
        getattr(protocol, method).assert_not_called()
