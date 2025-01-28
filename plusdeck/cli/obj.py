from dataclasses import dataclass

from plusdeck.cli.output import OutputMode
from plusdeck.config import Config


@dataclass
class Obj:
    """
    The main click context object. Contains options collated from parameters and the
    loaded config file.
    """

    config: Config
    global_: bool
    port: str
    output: OutputMode
