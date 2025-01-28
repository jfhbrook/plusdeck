from dataclasses import asdict, is_dataclass
from enum import Enum
import json
import logging
from typing import Any, Literal

try:
    from typing import Self
except ImportError:
    Self = Any

import click

from plusdeck.client import State

OutputMode = Literal["text"] | Literal["json"]

logger = logging.getLogger(__name__)


def as_json(obj: Any) -> Any:
    """
    Convert an object into something that is JSON-serializable.
    """

    if isinstance(obj, Enum):
        return obj.name
    elif is_dataclass(obj.__class__):
        return asdict(obj)
    else:
        return obj


class Echo:
    """
    An abstraction for writing output to the terminal. Used to support the
    behavior of the --output flag.
    """

    mode: OutputMode = "text"

    def __call__(self: Self, obj: Any, *args, **kwargs) -> None:
        if self.mode == "json":
            try:
                click.echo(json.dumps(as_json(obj), indent=2), *args, **kwargs)
            except Exception as exc:
                logger.debug(exc)
                click.echo(json.dumps(repr(obj)), *args, **kwargs)
        else:
            if isinstance(obj, State):
                obj = obj.name

            click.echo(
                obj if isinstance(obj, str) else repr(obj),
                *args,
                **kwargs,
            )


echo = Echo()
