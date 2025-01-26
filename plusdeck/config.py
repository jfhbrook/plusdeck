from configurence import BaseConfig, config, field, global_file
from serial.tools.list_ports import comports

"""
Configuration management for the Plus Deck 2C PC Cassette Deck. The client
doesn't use this directly, but it's useful when writing applications and
configuring the ipywidgets player.
"""

APP_NAME = "plusdeck"
GLOBAL_FILE = global_file(APP_NAME)


def default_port() -> str:
    """Get a default serial port."""

    return comports(include_links=True)[0].device


@config(APP_NAME)
class Config(BaseConfig):
    """A config for the Plus Deck 2C PC Cassette Deck."""

    port: str = field(default_factory=default_port, env_var="PORT")
