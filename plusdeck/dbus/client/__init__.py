from typing import Any, cast, Self
from unittest.mock import Mock

from plusdeck.config import Config
from plusdeck.dbus.config import StagedConfig
from plusdeck.dbus.domain import ConfigM
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface


class DbusClient(DbusInterface):
    """
    A DBus client for the Plus Deck 2C PC Cassette Deck.
    """

    def __init__(self: Self) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        self.subscribe = Mock(name="client.subscribe")
        super().__init__(client)

        cast(Any, self)._proxify(DBUS_NAME, "/")

    async def staged_config(self: Self) -> StagedConfig:
        """
        Fetch the state of staged configuration changes.
        """

        active_config: Config = ConfigM.unpack(await self.config)

        return StagedConfig(
            target_config=Config.from_file(active_config.file),
            active_config=active_config,
        )
