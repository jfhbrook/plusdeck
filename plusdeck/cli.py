import asyncio
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import functools
import json
import logging
import os
import sys
from typing import Any, Callable, Coroutine, List, Literal, Optional
import warnings

try:
    from typing import Self
except ImportError:
    Self = Any

import click
from serial.serialutil import SerialException

from plusdeck.client import Client, create_connection, State
from plusdeck.config import Config, GLOBAL_FILE

logger = logging.getLogger(__name__)

OutputMode = Literal["text"] | Literal["json"]


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
    timeout: Optional[float]


LogLevel = (
    Literal["DEBUG"]
    | Literal["INFO"]
    | Literal["WARNING"]
    | Literal["ERROR"]
    | Literal["CRITICAL"]
)

STATES: List[str] = [state.name for state in State]


class PlusdeckState(click.Choice):
    """
    A Plus Deck 2C state.
    """

    name = "state"

    def __init__(self: Self) -> None:
        super().__init__(STATES)

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> State:
        choice = super().convert(value, param, ctx)

        return State[choice]


STATE = PlusdeckState()


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
            click.echo(
                obj if isinstance(obj, str) else repr(obj),
                *args,
                **kwargs,
            )


echo = Echo()

AsyncCommand = Callable[..., Coroutine[None, None, None]]
WrappedAsyncCommand = Callable[..., None]
AsyncCommandDecorator = Callable[[AsyncCommand], WrappedAsyncCommand]


def pass_client(run_forever: bool = False) -> AsyncCommandDecorator:
    """
    Create a client and pass it to the decorated click handler.
    """

    def decorator(fn: AsyncCommand) -> WrappedAsyncCommand:
        @click.pass_obj
        @functools.wraps(fn)
        def wrapped(obj: Obj, *args, **kwargs) -> None:
            port: str = obj.port
            output = obj.output
            timeout = obj.timeout

            # Set the output mode for echo
            echo.mode = output

            async def main() -> None:
                try:
                    client: Client = await create_connection(port)
                except SerialException as exc:
                    click.echo(exc)
                    sys.exit(1)

                # Giddyup!
                try:
                    async with asyncio.timeout(timeout):
                        await fn(client, *args, **kwargs)
                except TimeoutError:
                    echo(f"Command timed out after {timeout} seconds.")
                    sys.exit(1)

                # Close the client if we're done
                if not run_forever:
                    client.close()

                # Await the client closing and surface any exceptions
                await client.closed

            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass

        return wrapped

    return decorator


@click.group()
@click.option(
    "--global/--no-global",
    "global_",
    default=os.geteuid() == 0,
    help=f"Load the global config file at {GLOBAL_FILE} "
    "(default true when called with sudo)",
)
@click.option("--config-file", "-C", type=click.Path(), help="A path to a config file")
@click.option(
    "--log-level",
    envvar="CRYSTALFONTZ_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
)
@click.option(
    "--port",
    envvar="CRYSTALFONTZ_PORT",
    help="The serial port the device is connected to",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output either human-friendly text or JSON",
)
@click.option(
    "--timeout",
    type=float,
    envvar="CRYSTALFONTZ_TIMEOUT",
    help="How long to wait for a response from the device before timing out",
)
@click.pass_context
def main(
    ctx: click.Context,
    global_: bool,
    config_file: Optional[str],
    log_level: LogLevel,
    port: Optional[str],
    output: Optional[OutputMode],
    timeout: Optional[float],
) -> None:
    """
    Control your Crystalfontz device.
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
        timeout=timeout or config.timeout,
    )

    logging.basicConfig(level=getattr(logging, log_level))


@main.group
def play() -> None:
    """
    Play a tape
    """


@play.command(name="a")
@pass_client()
async def play_a(client: Client) -> None:
    """
    Play side A of the tape
    """

    client.play_a()


@play.command(name="b")
@pass_client()
async def play_b(client: Client) -> None:
    """
    Play side B of the tape
    """

    client.play_b()


@main.group
def fast_forward() -> None:
    """
    Fast-forward a tape
    """


@fast_forward.command(name="a")
@pass_client()
async def fast_forward_a(client: Client) -> None:
    """
    Fast-forward side A of the tape
    """

    client.fast_forward_a()


@fast_forward.command(name="b")
@pass_client()
async def fast_forward_b(client: Client) -> None:
    """
    Fast-forward side B of the tape
    """

    client.fast_forward_b()


@main.group
def rewind() -> None:
    """
    Rewind a tape
    """


@rewind.command(name="a")
@pass_client()
async def rewind_a(client: Client) -> None:
    """
    Rewind side A of the tape
    """

    client.rewind_a()


@rewind.command(name="b")
@pass_client()
async def rewind_b(client: Client) -> None:
    """
    Rewind side B of the tape
    """

    client.rewind_b()


@main.command
@pass_client()
async def pause(client: Client) -> None:
    """
    Pause the tape
    """

    client.pause()


@main.command
@pass_client()
async def stop(client: Client) -> None:
    """
    Stop the tape
    """

    client.stop()


@main.command
@pass_client()
async def eject(client: Client) -> None:
    """
    Eject the tape
    """

    client.eject()


@main.command
@click.argument("state", type=STATE)
@pass_client()
async def expect(client: Client, state: State) -> None:
    """
    Wait for an expected state
    """

    async with client.session() as rcv:
        await rcv.expect(state)


@main.command
@pass_client(run_forever=True)
async def listen(client: Client) -> None:
    """
    Listen for state change events
    """

    async with client.session() as rcv:
        async for state in rcv:
            echo(state)
