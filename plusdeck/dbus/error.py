from contextlib import asynccontextmanager
from logging import Logger
import re
import sys
from traceback import format_exc
from typing import Any, AsyncGenerator, cast, List, Optional

from sdbus.sd_bus_internals import (  # pyright: ignore [reportMissingModuleSource]
    SdBusLibraryError,
)

ERROR_NUMBER_RE = r"returned error number: (\d+)"


@asynccontextmanager
async def handle_dbus_error(logger: Logger) -> AsyncGenerator[None, None]:
    try:
        yield
    except Exception as exc:
        exit_code: Optional[int] = None
        if isinstance(exc, SdBusLibraryError):
            logger.debug(format_exc())

            error_numbers: List[str] = re.findall(ERROR_NUMBER_RE, str(exc))
            exit_code = int(error_numbers[0]) if error_numbers else 1

            logger.error(f"SdBusLibraryError: {exc}")
        elif hasattr(exc, "dbus_error_name"):
            exit_code = 1
            dbus_error_name = cast(Any, exc).dbus_error_name
            dbus_msg = str(exc)
            if dbus_msg:
                logger.error(f"{dbus_error_name}: {dbus_msg}")
            else:
                logger.error(f"{dbus_error_name}")

        if exit_code is not None:
            sys.exit(exit_code)

        raise exc
