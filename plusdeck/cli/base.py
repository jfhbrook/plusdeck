import logging
import os
from typing import Optional
import warnings

import click

from plusdeck.cli.logger import LogLevel
from plusdeck.cli.obj import Obj
from plusdeck.cli.output import OutputMode
from plusdeck.config import Config, GLOBAL_FILE


def main_group() -> click.Group:
    @click.group()
    @click.option(
        "--global/--no-global",
        "global_",
        default=os.geteuid() == 0,
        help=f"Load the global config file at {GLOBAL_FILE} "
        "(default true when called with sudo)",
    )
    @click.option(
        "--config-file", "-C", type=click.Path(), help="A path to a config file"
    )
    @click.option(
        "--log-level",
        envvar="PLUSDECK_LOG_LEVEL",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        default="INFO",
        help="Set the log level",
    )
    @click.option(
        "--port",
        envvar="PLUSDECK_PORT",
        help="The serial port the device is connected to",
    )
    @click.option(
        "--output",
        type=click.Choice(["text", "json"]),
        default="text",
        help="Output either human-friendly text or JSON",
    )
    @click.pass_context
    def main(
        ctx: click.Context,
        global_: bool,
        config_file: Optional[str],
        log_level: LogLevel,
        port: Optional[str],
        output: Optional[OutputMode],
    ) -> None:
        """
        Control your Plus Deck 2C tape deck.
        """

        file = None
        if config_file:
            if global_:
                warnings.warn(
                    "--config-file is specified, so --global flag will be ignored."
                )
            file = config_file
        elif global_:
            file = GLOBAL_FILE
        config: Config = Config.from_file(file=file)
        ctx.obj = Obj(
            config=config,
            global_=global_,
            port=port or config.port,
            output=output or "text",
        )

        logging.basicConfig(level=getattr(logging, log_level))

    return main
