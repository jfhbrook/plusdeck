from collections.abc import AsyncIterator
from typing import Any, Callable, Self, Type


class Property:
    def __init__(self: Self, fn: Any) -> None:
        self._fn = fn

    async def get_async(self: Self) -> Any:
        return self._fn()

    async def set_async(self: Self, value: Any) -> None:
        raise NotImplementedError("set_async")


class Signal(AsyncIterator):
    def emit(self: Self, obj: Any) -> None:
        pass

    async def __anext__(self: Self) -> str:
        raise NotImplementedError("__anext__")


def dbus_method_async(*args, **kwargs) -> Any:
    def decorator(f: Any) -> Any:
        return f

    return decorator


def dbus_property_async(*args, **kwargs) -> Callable[[Any], Property]:
    def decorator(fn: Any) -> Property:
        return Property(fn)

    return decorator


def dbus_signal_async(*args, **kwargs) -> Callable[[Any], Signal]:
    def decorator(f: Any) -> Any:
        return Signal()

    return decorator


class DbusInterfaceCommonAsync:
    def __init_subclass__(cls: Type[Self], *args, **kwargs) -> None:
        pass

    def export_to_dbus(self: Self, path: str) -> None:
        pass

    def _proxyify(self: Self, name: str, path: str) -> None:
        pass


async def request_default_bus_name_async(bus_name: str) -> None:
    pass
