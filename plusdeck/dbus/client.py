import asyncio
import functools
import logging
import sys
from typing import Any, Optional
from unittest.mock import Mock

try:
    from typing import Self
except ImportError:
    Self = Any

import click

from plusdeck.cli.client import AsyncCommand, WrappedAsyncCommand
from plusdeck.cli.logger import LogLevel
from plusdeck.cli.obj import Obj
from plusdeck.cli.output import echo, OutputMode
from plusdeck.cli.types import STATE
from plusdeck.client import State
from plusdeck.dbus.interface import DBUS_NAME, DbusInterface

logger = logging.getLogger(__name__)


class DbusClient(DbusInterface):
    """
    Plus Deck 2C dbus client.
    """

    def __init__(self: Self) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        super().__init__(client)
        self._proxify(DBUS_NAME, "/")


def pass_client(fn: AsyncCommand) -> WrappedAsyncCommand:
    """
    Create a dbus client and pass it to the decorated click handler.
    """

    @click.pass_obj
    @functools.wraps(fn)
    def wrapped(obj: Obj, *args, **kwargs) -> None:
        output = obj.output

        # Set the output mode for echo
        echo.mode = output

        async def main() -> None:
            client: DbusClient = DbusClient()

            # Giddyup!
            await fn(client, *args, **kwargs)

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

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
    global_: bool,
    config_file: Optional[str],
    log_level: LogLevel,
    port: Optional[str],
    output: Optional[OutputMode],
) -> None:
    """
    Control your Plus Deck 2C Cassette Drive through dbus.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    raise NotImplementedError("main")

    # TODO: We don't actually need/want obj. Instead, we want to:
    #
    # 1. Set up the client
    # 2. Get the config file path from the dbus client
    # 3. Load the config based on that file path
    #
    # This implies that we want a separate Obj implementation with a client
    # and a config attached to it.

    config: Config = Config.from_file(file=file)
    ctx.obj = Obj(
        config=config,
        global_=global_,
        port=port or config.port,
        output=output or "text",
    )


@main.group()
def config() -> None:
    """
    Configure plusdeck.
    """
    pass


@config.command()
@click.argument("name")
@pass_client
@click.pass_obj
async def get(obj: Obj, client: DbusClient, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(obj.config.get(name))
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)

    await client.reload()


@config.command()
@click.pass_obj
def show(obj: Obj) -> None:
    """
    Show the current configuration.
    """
    echo(obj.config)


@config.command()
@click.argument("name")
@click.argument("value")
@pass_client
@click.pass_obj
async def set(obj: Obj, client: DbusClient, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """
    try:
        obj.config.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    obj.config.to_file()

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
async def expect(client: DbusClient, state: State, timeout: Optional[float]) -> None:
    """
    Wait for an expected state
    """

    # TODO: Does dbus client support wait_for?
    await client.wait_for(state.name, timeout if timeout is not None else -1)


@main.command
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@pass_client
@click.pass_obj
async def subscribe(obj: Obj, client: DbusClient, for_: Optional[float]) -> None:
    """
    Subscribe to state changes
    """

    # TODO: What's the best way to support this?
    raise NotImplementedError("subscribe")
