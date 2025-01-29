import asyncio
from collections.abc import AsyncIterable
from dataclasses import dataclass
import functools
import inspect
import logging
import sys
from typing import cast, Optional, Self
from unittest.mock import Mock

import click

from plusdeck.cli import (
    AsyncCommand,
    echo,
    LogLevel,
    OutputMode,
    STATE,
    WrappedAsyncCommand,
)
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
        self._proxify(DBUS_NAME, "/")


@dataclass
class Obj:
    """
    The main click context object. Contains options collated from parameters and the
    loaded config file.
    """

    client: DbusClient
    output: OutputMode
    _config: Optional[Config] = None

    async def config(self: Self) -> Config:
        if not self._config:
            config_file = await self.client.config_file

            self._config = Config.from_file(config_file)

        return self._config


def async_command(fn: AsyncCommand) -> WrappedAsyncCommand:
    """
    Create a dbus client and pass it to the decorated click handler.
    """

    @click.pass_obj
    @functools.wraps(fn)
    def wrapped(obj: Obj, *args, **kwargs) -> None:
        async def main() -> None:
            # Giddyup!
            await fn(obj.client, *args, **kwargs)

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

    return wrapped


def pass_config(fn: AsyncCommand) -> WrappedAsyncCommand:
    """
    Create a dbus client and pass it to the decorated click handler.
    """

    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        config = await obj.config()
        return fn(config, *args, **kwargs)

    return wrapped


def pass_client(fn: AsyncCommand) -> WrappedAsyncCommand:
    """
    Create a dbus client and pass it to the decorated click handler.
    """

    @click.pass_obj
    @functools.wraps(fn)
    def wrapped(obj: Obj, *args, **kwargs) -> None:
        return fn(obj.client, *args, **kwargs)

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


@main.group()
def config() -> None:
    """
    Configure plusdeck.
    """
    pass


@config.command()
@click.argument("name")
@click.pass_config
def get(config: Config, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(config.get(name))
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)


@config.command()
@click.pass_config
def show(config: Config) -> None:
    """
    Show the current configuration.
    """
    echo(config)


@config.command()
@click.argument("name")
@click.argument("value")
@pass_config
@pass_client
@async_command
async def set(config: Config, client: DbusClient, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """

    try:
        config.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    config.to_file()

    await client.reload()


@config.command()
@click.argument("name")
@pass_client
@click.pass_obj
async def unset(obj: Obj, client: DbusClient, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        obj.config.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    obj.config.to_file()

    await client.reload()


@main.group
def play() -> None:
    """
    Play a tape
    """


@play.command(name="a")
@pass_client
async def play_a(client: DbusClient) -> None:
    """
    Play side A of the tape
    """

    await client.play_a()


@play.command(name="b")
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
@pass_client
async def fast_forward_a(client: DbusClient) -> None:
    """
    Fast-forward side A of the tape
    """

    await client.fast_forward_a()


@fast_forward.command(name="b")
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
@pass_client
async def rewind_a(client: DbusClient) -> None:
    """
    Rewind side A of the tape
    """

    await client.rewind_a()


@rewind.command(name="b")
@pass_client
async def rewind_b(client: DbusClient) -> None:
    """
    Rewind side B of the tape
    """

    await client.rewind_b()


@main.command
@pass_client
async def pause(client: DbusClient) -> None:
    """
    Pause the tape
    """

    await client.pause()


@main.command
@pass_client
async def stop(client: DbusClient) -> None:
    """
    Stop the tape
    """

    await client.stop()


@main.command
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
@pass_client
async def wait_for(client: DbusClient, state: State, timeout: Optional[float]) -> None:
    """
    Wait for an expected state
    """

    await client.wait_for(state.name, timeout if timeout is not None else -1)


@main.command
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@pass_client
@click.pass_obj
async def subscribe(obj: Obj, client: DbusClient, for_: Optional[float]) -> None:
    """
    Subscribe to state changes
    """

    try:
        async with asyncio.timeout(for_):
            # TODO: Why is this unhappy?
            async for st in cast(AsyncIterable, client.state):
                echo(State[st])
    except TimeoutError:
        pass
