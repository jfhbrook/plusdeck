from dataclasses import asdict, dataclass, field, fields, replace
import os
import os.path
from typing import Any, Dict, Optional, Type

from appdirs import user_config_dir
from serial.tools.list_ports import comports
import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

APP_NAME = "plusdeck"


def default_file() -> str:
    """Get the default file path for the Plus Deck 2C client config."""

    return os.path.join(user_config_dir(APP_NAME), f"{APP_NAME}.yaml")


def default_port() -> str:
    """Get a default serial port."""

    return comports(include_links=True)[0].device


def _metadata(env_var: Optional[str] = None) -> Dict[str, Any]:
    return dict(env_var=env_var)


def _from_environment() -> Dict[str, Any]:
    env: Dict[str, Any] = dict()
    for f in fields(Config):
        if f.metadata and "env_var" in f.metadata:
            if f.metadata["env_var"] in os.environ:
                env[f.name] = os.environ[f.metadata["env_var"]]
    return env


@dataclass
class Config:
    """A config for the Plus Deck 2C PC Cassette Deck."""

    port: str = field(
        default_factory=default_port, metadata=_metadata(env_var="PLUSDECK_PORT")
    )
    file: Optional[str] = None

    @classmethod
    def from_environment(cls: Type["Config"]) -> "Config":
        """Load a config from the environment."""

        return cls(**_from_environment())

    @classmethod
    def from_file(
        cls: Type["Config"],
        file: Optional[str] = None,
        load_environment: bool = False,
        create_file: bool = False,
    ) -> "Config":
        """Load a config from a file."""

        _file: str = file or os.environ.get("PLUSDECK_CONFIG", default_file())

        found_file = False
        kwargs = dict(file=_file)
        try:
            with open(_file, "r") as f:
                found_file = True
                kwargs.update(yaml.load(f, Loader=Loader))
        except FileNotFoundError:
            pass

        if load_environment:
            kwargs.update(_from_environment())

        config = cls(**kwargs)

        if not found_file and create_file:
            config.to_file()

        return config

    def to_file(self, file: Optional[str] = None) -> "Config":
        """Save the config to a file."""

        file = file or self.file or default_file()

        with open(file, "w") as f:
            yaml.dump(asdict(self), f, Dumper=Dumper)

        return replace(self, file=file)
