import asyncio
from dataclasses import asdict, dataclass, is_dataclass
import logging
import os
import sys
from typing import (
    Any,
    Callable,
    cast,
    Coroutine,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
)

try:
    from typing import Self
except ImportError:
    Self = Any

import click
from serial.serialutil import SerialException

from plusdeck.config import Config, GLOBAL_FILE


logger = logging.getLogger(__name__)

@dataclass
class Obj:
    """
    The main click context object. Contains options collated from parameters and the
    loaded config file.
    """

    config: Config
    global_: bool
    port: str
    model: str
    hardware_rev: Optional[str]
    firmware_rev: Optional[str]
    output: OutputMode
    timeout: Optional[float]
    retry_times: Optional[int]
    baud_rate: BaudRate
    effect_options: Optional[EffectOptions] = None

LogLevel = (
    Literal["DEBUG"]
    | Literal["INFO"]
    | Literal["WARNING"]
    | Literal["ERROR"]
    | Literal["CRITICAL"]
)


def as_json(obj: Any) -> Any:
    """
    Convert an object into something that is JSON-serializable.
    """
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    elif is_dataclass(obj.__class__):
        return asdict(obj)
    elif isinstance(obj, bytes):
        return format_json_bytes(obj)
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
                obj if isinstance(obj, bytes) or isinstance(obj, str) else repr(obj),
                *args,
                **kwargs,
            )


echo = Echo()

AsyncCommand = Callable[..., Coroutine[None, None, None]]
WrappedAsyncCommand = Callable[..., None]
AsyncCommandDecorator = Callable[[AsyncCommand], WrappedAsyncCommand]


def pass_client(
    run_forever: bool = False,
    report_handler_cls: Type[ReportHandler] = NoopReportHandler,
) -> AsyncCommandDecorator:
    """
    Create a client and pass it to the decorated click handler.
    """

    def decorator(fn: AsyncCommand) -> WrappedAsyncCommand:
        @click.pass_obj
        @functools.wraps(fn)
        def wrapped(obj: Obj, *args, **kwargs) -> None:
            port: str = obj.port
            model = obj.model
            hardware_rev = obj.hardware_rev
            firmware_rev = obj.firmware_rev
            output = obj.output
            timeout = obj.timeout
            retry_times = obj.retry_times
            baud_rate: BaudRate = obj.baud_rate

            report_handler = report_handler_cls()

            # Set the output mode on the report handler
            if isinstance(report_handler, CliReportHandler):
                report_handler.mode = output

            # Set the output mode for echo
            echo.mode = output

            async def main() -> None:
                try:
                    client: Client = await create_connection(
                        port,
                        model=model,
                        hardware_rev=hardware_rev,
                        firmware_rev=firmware_rev,
                        report_handler=report_handler,
                        timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
                        retry_times=(
                            retry_times
                            if retry_times is not None
                            else DEFAULT_RETRY_TIMES
                        ),
                        baud_rate=baud_rate,
                    )
                except SerialException as exc:
                    click.echo(exc)
                    sys.exit(1)

                # Giddyup!
                try:
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
    "--model",
    envvar="CRYSTALFONTZ_MODEL",
    help="The model of the device",
    type=click.Choice(["CFA533", "CFA633"]),
    default="CFA533",
)
@click.option(
    "--hardware-rev",
    envvar="CRYSTALFONTZ_HARDWARE_REV",
    help="The hardware revision of the device",
)
@click.option(
    "--firmware-rev",
    envvar="CRYSTALFONTZ_FIRMWARE_REV",
    help="The firmware revision of the device",
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
@click.option(
    "--retry-times",
    type=int,
    envvar="CRYSTALFONTZ_RETRY_TIMES",
    help="How many times to retry a command if a response times out",
)
@click.option(
    "--baud",
    type=click.Choice([str(SLOW_BAUD_RATE), str(FAST_BAUD_RATE)]),
    envvar="CRYSTALFONTZ_BAUD_RATE",
    help="The baud rate to use when connecting to the device",
)
@click.pass_context
def main(
    ctx: click.Context,
    global_: bool,
    config_file: Optional[str],
    log_level: LogLevel,
    port: Optional[str],
    model: str,
    hardware_rev: Optional[str],
    firmware_rev: Optional[str],
    output: Optional[OutputMode],
    timeout: Optional[float],
    retry_times: Optional[int],
    baud: Optional[str],
) -> None:
    """
    Control your Crystalfontz device.
    """

    baud_rate = cast(Optional[BaudRate], int(baud) if baud else None)
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
        model=model or config.model,
        hardware_rev=hardware_rev or config.hardware_rev,
        firmware_rev=firmware_rev or config.firmware_rev,
        output=output or "text",
        timeout=timeout or config.timeout,
        retry_times=retry_times if retry_times is not None else config.retry_times,
        baud_rate=baud_rate or config.baud_rate,
    )

    logging.basicConfig(level=getattr(logging, log_level))



