import asyncio
from dataclasses import dataclass
import functools
import logging
import sys
from typing import Any, cast, Optional, Self
from unittest.mock import Mock

import click

from plusdeck.cli import async_command, AsyncCommand, echo, LogLevel, OutputMode, STATE
from plusdeck.client import State
from plusdeck.config import Config
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface

logger = logging.getLogger(__name__)


class DbusClient(DbusInterface):
    """
    Plus Deck 2C dbus client.
    """

    def __init__(self: Self) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        super().__init__("", client)
        cast(Any, self)._proxify(DBUS_NAME, "/")


@dataclass
class Obj:
    """
    The main click context object. Includes a dbus client and the ability to load
    the service's active config file.
    """

    client: DbusClient
    output: OutputMode
    _config: Optional[Config] = None

    async def config(self: Self) -> Config:
        if not self._config:
            config_file: str = await self.client.config_file
            config: Config = Config.from_file(config_file)
            self._config = config
            return config
        else:
            return self._config


def pass_config(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        config = await obj.config()
        await fn(config, *args, **kwargs)

    return wrapped


def pass_client(fn: AsyncCommand) -> AsyncCommand:
    """
    Create a dbus client and pass it to the decorated click handler.
    """

    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        return await fn(obj.client, *args, **kwargs)

    return wrapped


@click.group()
@click.option(
    "--log-level",
    envvar="PLUSDECK_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
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
    log_level: LogLevel,
    output: OutputMode,
) -> None:
    """
    Control your Plus Deck 2C Cassette Drive through dbus.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    # Set the output mode for echo
    echo.mode = output

    client = DbusClient()

    ctx.obj = Obj(client=client, output=output)


def warn_configuration_unsynced() -> None:
    logger.warn(
        """The service configuration is out of sync. To reload the service, run:

    sudo systemctl restart plusdeck"""
    )


@main.group()
def config() -> None:
    """
    Configure plusdeck.
    """
    pass


@config.command()
@click.argument("name")
@async_command
@pass_config
async def get(config: Config, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(config.get(name))
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)


@config.command()
@async_command
@pass_config
async def show(config: Config) -> None:
    """
    Show the current configuration.
    """
    echo(config)

    # TODO: Show unsynced configuration
    # TODO: Call warn_configuration_unsynced if configuration out of sync


@config.command()
@click.argument("name")
@click.argument("value")
@async_command
@pass_config
async def set(config: Config, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """

    try:
        config.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    config.to_file()

    warn_configuration_unsynced()


@config.command()
@click.argument("name")
@async_command
@pass_config
async def unset(config: Config, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        config.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    config.to_file()

    warn_configuration_unsynced()


@main.group
def play() -> None:
    """
    Play a tape
    """


@play.command(name="a")
@async_command
@pass_client
async def play_a(client: DbusClient) -> None:
    """
    Play side A of the tape
    """

    await client.play_a()


@play.command(name="b")
@async_command
@pass_client
async def play_b(client: DbusClient) -> None:
    """
    Play side B of the tape
    """

    await client.play_b()


@main.group
def fast_forward() -> None:
    """
    Fast-forward a tape
    """


@fast_forward.command(name="a")
@async_command
@pass_client
async def fast_forward_a(client: DbusClient) -> None:
    """
    Fast-forward side A of the tape
    """

    await client.fast_forward_a()


@fast_forward.command(name="b")
@async_command
@pass_client
async def fast_forward_b(client: DbusClient) -> None:
    """
    Fast-forward side B of the tape
    """

    await client.fast_forward_b()


@main.group
def rewind() -> None:
    """
    Rewind a tape
    """


@rewind.command(name="a")
@async_command
@pass_client
async def rewind_a(client: DbusClient) -> None:
    """
    Rewind side A of the tape
    """

    await client.rewind_a()


@rewind.command(name="b")
@async_command
@pass_client
async def rewind_b(client: DbusClient) -> None:
    """
    Rewind side B of the tape
    """

    await client.rewind_b()


@main.command
@async_command
@pass_client
async def pause(client: DbusClient) -> None:
    """
    Pause the tape
    """

    await client.pause()


@main.command
@async_command
@pass_client
async def stop(client: DbusClient) -> None:
    """
    Stop the tape
    """

    await client.stop()


@main.command
@async_command
@pass_client
async def eject(client: DbusClient) -> None:
    """
    Eject the tape
    """

    await client.eject()


@main.command
@click.argument("state", type=STATE)
@click.option(
    "--timeout",
    type=float,
    help="How long to wait for a state change from the Plus Deck 2C before timing out",
)
@async_command
@pass_client
async def expect(client: DbusClient, state: State, timeout: Optional[float]) -> None:
    """
    Wait for an expected state
    """

    await client.wait_for(state.name, timeout if timeout is not None else -1)


@main.command
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@async_command
@pass_client
async def subscribe(client: DbusClient, for_: Optional[float]) -> None:
    """
    Subscribe to state changes
    """

    try:
        async with asyncio.timeout(for_):
            async for st in client.state:
                echo(State[st])
    except TimeoutError:
        pass
