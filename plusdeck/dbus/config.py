from dataclasses import asdict, dataclass, fields
import json
from typing import Any, Dict, Generic, Literal, Self, Tuple, TypeVar

import yaml

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from plusdeck.config import Config

File = str
Port = str
ConfigPayload = Tuple[File, Port]

StageType = Literal["set"] | Literal["unset"] | None
T = TypeVar("T")


@dataclass
class StagedAttr(Generic[T]):
    type: StageType
    active: T
    target: T

    def __repr__(self: Self) -> str:
        target: str = (
            self.target if type(self.target) is str else json.dumps(self.target)
        )

        if self.type is None:
            return target

        active: str = (
            self.active if type(self.active) is str else json.dumps(self.active)
        )

        return f"{active} ~> {target}"


class StagedConfig:
    def __init__(self: Self, active_config: Config, target_config: Config) -> None:
        # The configuration currently loaded by the service
        self.active_config: Config = active_config
        # The configuration as per the file
        self.target_config: Config = target_config
        self.dirty = False

    def get(self: Self, name: str) -> StagedAttr[Any]:
        active_attr = self.active_config.get(name)
        target_attr = self.target_config.get(name)

        type_: StageType = None
        if active_attr != target_attr:
            if target_attr is None:
                type_ = "unset"
            else:
                type_ = "set"

        return StagedAttr(type=type_, active=active_attr, target=target_attr)

    def set(self: Self, name: str, value: str) -> None:
        self.target_config.set(name, value)
        if self.target_config.get(name) != self.active_config.get(name):
            self.dirty = True

    def unset(self: Self, name: str) -> None:
        self.target_config.unset(name)
        if self.target_config.get(name) != self.active_config.get(name):
            self.dirty = True

    def as_dict(self: Self) -> Dict[str, Any]:
        d: Dict[str, Any] = dict()

        for f in fields(self.target_config):
            d[f.name] = asdict(self.get(f.name))

        return d

    def __repr__(self: Self) -> str:
        d: Dict[str, Any] = dict()

        for f in fields(self.target_config):
            d[f.name] = repr(self.get(f.name))

        dump = yaml.dump(d, Dumper=Dumper)
        return "\n".join(
            [f"~ {line}" if "~>" in line else f"  {line}" for line in dump.split("\n")]
        )

    def to_file(self: Self) -> None:
        self.target_config.to_file()
