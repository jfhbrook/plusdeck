from typing import Any
from unittest.mock import Mock

try:
    from typing import Self
except ImportError:
    Self = Any

from plusdeck.dbus.interface import DBUS_NAME, PlusdeckInterface


class PlusdeckClient(PlusdeckInterface):
    def __init__(self: Self) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        super().__init__(client)
        self._proxify(DBUS_NAME, "/")
