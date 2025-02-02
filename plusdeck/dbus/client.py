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
from plusdeck.dbus.config import StagedConfig
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface

logger = logging.getLogger(__name__)


class DbusClient(DbusInterface):
    """
    Plus Deck 2C dbus client.
    """

    def __init__(self: Self) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        self.subscribe = Mock(name="client.subscribe")
        super().__init__("", client)

        cast(Any, self)._proxify(DBUS_NAME, "/")

    async def staged_config(self: Self) -> StagedConfig:
        file, port = await self.config

        active_config: Config = cast(Any, Config)(file=file, port=port)

        return StagedConfig(
            target_config=Config.from_file(self._config.file),
            active_config=active_config,
        )


@dataclass
class Obj:
    """
    The main click context object. Includes a dbus client and the ability to load
    the service's active config file.
    """

    client: DbusClient
    output: OutputMode


def pass_config(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        config = await obj.client.staged_config()
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

    async def load() -> None:
        client = DbusClient()
        ctx.obj = Obj(client=client, output=output)

    asyncio.run(load())


def warn_dirty() -> None:
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
async def get(staged: StagedConfig, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(staged.get(name))
    except ValueError as exc:
        echo(str(exc))
        raise SystemExit(1)
    finally:
        if staged.dirty:
            warn_dirty()


@config.command()
@async_command
@pass_config
async def show(staged: StagedConfig) -> None:
    """
    Show the current configuration.
    """
    echo(staged)

    if staged.dirty:
        warn_dirty()


@config.command()
@click.argument("name")
@click.argument("value")
@async_command
@pass_config
async def set(staged: StagedConfig, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """

    try:
        staged.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    else:
        staged.to_file()
    finally:
        if staged.dirty:
            warn_dirty()


@config.command()
@click.argument("name")
@async_command
@pass_config
async def unset(staged: StagedConfig, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        staged.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    else:
        staged.to_file()
    finally:
        if staged.dirty:
            warn_dirty()


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
