import asyncio
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import functools
import json
import logging
import os
import sys
from typing import Any, Callable, Coroutine, List, Literal, Optional, Self
import warnings

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
            if isinstance(obj, State):
                obj = obj.name

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

            # Set the output mode for echo
            echo.mode = output

            async def main() -> None:
                try:
                    client: Client = await create_connection(port)
                except SerialException as exc:
                    click.echo(exc)
                    sys.exit(1)

                # Giddyup!
                await fn(client, *args, **kwargs)

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


@main.group()
def config() -> None:
    """
    Configure plusdeck.
    """
    pass


@config.command()
@click.argument("name")
@click.pass_obj
def get(obj: Obj, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(obj.config.get(name))
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)


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
@click.pass_obj
def set(obj: Obj, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """
    try:
        obj.config.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    obj.config.to_file()


@config.command()
@click.argument("name")
@click.pass_obj
def unset(obj: Obj, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        obj.config.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    obj.config.to_file()


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
@click.option(
    "--timeout",
    type=float,
    help="How long to wait for a state change from the Plus Deck 2C before timing out",
)
@pass_client()
async def expect(client: Client, state: State, timeout: Optional[float]) -> None:
    """
    Wait for an expected state
    """

    async with client.session() as rcv:
        try:
            await rcv.expect(state, timeout=timeout)
        except TimeoutError:
            logger.info(f"Timed out after {timeout} seconds.")


@main.command
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@pass_client(run_forever=True)
@click.pass_obj
async def subscribe(obj: Obj, client: Client, for_: Optional[float]) -> None:
    """
    Subscribe to state changes
    """

    running = True

    async def subscribe() -> None:
        async with client.session() as rcv:
            while True:
                if not running:
                    break
                try:
                    state = await rcv.get_state(timeout=1.0)
                    echo(state)
                except TimeoutError:
                    pass

    subscription = client.loop.create_task(subscribe())

    if for_ is not None:
        await asyncio.sleep(for_)
        running = False
        await subscription
        client.close()
        await client.closed
    else:
        await subscription
