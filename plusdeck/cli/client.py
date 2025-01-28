import asyncio
import functools
import sys
from typing import Callable, Coroutine

import click
from serial.serialutil import SerialException

from plusdeck.cli.obj import Obj
from plusdeck.cli.output import echo
from plusdeck.client import Client, create_connection

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
