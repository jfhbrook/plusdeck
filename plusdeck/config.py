from configurence import config, field
from serial.tools.list_ports import comports

"""
Configuration management for the Plus Deck 2C PC Cassette Deck. The client
doesn't use this directly, but it's useful when writing applications and
configuring the ipywidgets player.
"""

APP_NAME = "plusdeck"


def default_port() -> str:
    """Get a default serial port."""

    return comports(include_links=True)[0].device


@config
class Config:
    """A config for the Plus Deck 2C PC Cassette Deck."""

    port: str = field(
        default_factory=default_port, env_var="PLUSDECK_PORT"
    )
