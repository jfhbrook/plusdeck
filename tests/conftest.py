# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pytest

from plusdeck.client import Client, State


@pytest.fixture
async def client():
    client = Client()
    client._transport = Mock(name="client._transport")
    client.state = State.Subscribed
    return client
