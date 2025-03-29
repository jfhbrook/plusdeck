# -*- coding: utf-8 -*-

import os
import os.path
from typing import Callable, Never
from unittest.mock import Mock

import pytest
from rich.prompt import Prompt

from plusdeck.client import Client, State
import plusdeck.config


@pytest.fixture
async def client():
    client = Client()
    client._transport = Mock(name="client._transport")
    client.state = State.SUBSCRIBED
    return client


@pytest.fixture
def environment(monkeypatch, config_file):
    environ = dict(PLUSDECK_CONFIG=config_file, PLUSDECK_PORT="/dev/ttyUSB1")
    monkeypatch.setattr(os, "environ", environ)
    return environ


@pytest.fixture
def config_file(monkeypatch):
    file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures", "config.yaml"
    )

    def default_file() -> str:
        return file

    monkeypatch.setattr(plusdeck.config, "default_file", default_file)

    return file


@pytest.fixture
def port(monkeypatch):
    port = "/dev/ttyUSB0"

    def default_port() -> str:
        return port

    monkeypatch.setattr(plusdeck.config, "default_port", default_port)

    return port


#
# Integration test fixtures
#


class AbortError(AssertionError):
    """
    A manual testing step has been aborted.
    """

    pass


@pytest.fixture
def abort() -> Callable[[], Never]:
    """
    Abort a GAK test.
    """

    def _abort() -> Never:
        raise AbortError("Aborted.")

    return _abort


@pytest.fixture
def confirm(abort, capsys) -> Callable[[str], None]:
    """
    Manually confirm an expected state.
    """

    def _confirm(text: str) -> None:
        with capsys.disabled():
            res = Prompt.ask(text, choices=["confirm", "abort"])

        if res == "abort":
            abort()

    return _confirm


@pytest.fixture
def take_action(abort, capsys) -> Callable[[str], None]:
    """
    Take a manual action before continuing.
    """

    def _take_action(text: str) -> None:
        with capsys.disabled():
            res = Prompt.ask(text, choices=["continue", "abort"])

        if res == "abort":
            abort()

    return _take_action


@pytest.fixture
def check(abort, capsys) -> Callable[[str, str], None]:
    """
    Manually check whether or not an expected state is so.
    """

    def _check(text: str, expected: str) -> None:
        with capsys.disabled():
            res = Prompt.ask(text, choices=["yes", "no", "abort"])

        if res == "abort":
            abort()

        assert res == "yes", expected

    return _check
