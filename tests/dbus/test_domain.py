from typing import Any, Callable, cast, List, Union

import pytest

from plusdeck.client import State
from plusdeck.config import Config
from plusdeck.dbus.domain import (
    ConfigM,
    OptFloatM,
    OptStrM,
    StateM,
    struct,
    t,
    TimeoutM,
    TypeProtocol,
)


@pytest.mark.parametrize(
    "fn,args,signature",
    [
        (t, ["s", "b", OptStrM, OptFloatM], "sbsd"),
        (struct, ["sss"], "(sss)"),
    ],
)
def test_signature_fn(
    fn: Callable[[Any], str], args: List[Union[str, TypeProtocol]], signature: str
) -> None:
    assert fn(*args) == signature


@pytest.mark.parametrize(
    "entity,map_cls",
    [
        (1.0, OptFloatM),
        (None, OptFloatM),
        (1.0, TimeoutM),
        (None, TimeoutM),
        (State.PLAYING_A, StateM),
        (
            cast(Any, Config)(
                file="/etc/crystalfontz.yaml",
                port="/dev/ttyUSB1",
            ),
            ConfigM,
        ),
    ],
)
def test_domain_pack_unpack(entity: Any, map_cls: Any, snapshot) -> None:
    packed = map_cls.pack(entity)

    assert packed == snapshot

    if hasattr(map_cls, "unpack"):
        unpacked = map_cls.unpack(packed)
        assert unpacked == entity
