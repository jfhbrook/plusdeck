# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pytest

from plusdeck import Client


@pytest.fixture
async def client():
    client = Client()
    client._transport = Mock(name="client._transport")
    return client