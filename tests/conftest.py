# -*- coding: utf-8 -*-

import os
import os.path
from unittest.mock import Mock

import pytest

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
