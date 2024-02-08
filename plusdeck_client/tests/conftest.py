# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pytest

from plusdeck_client import PlusDeckProtocol


@pytest.fixture
def protocol(event_methods):
    proto = PlusDeckProtocol()
    proto._transport = Mock(name="protocol._transport")

    proto.on_state = Mock(name="protocol.on_state")

    for method in event_methods:
        setattr(proto, method, Mock(name=f"protocol.{method}"))

    yield proto


@pytest.fixture
def event_methods():
    yield {
        "on_ready",
        "on_play",
        "on_pause",
        "on_stop",
        "on_fast_forward",
        "on_rewind",
        "on_eject",
        "on_off",
    }
