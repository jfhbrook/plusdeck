from typing import Any, Type

try:
    from typing import Self
except ImportError:
    Self = Any


class Signal:
    def emit(self: Self, obj: Any) -> None:
        pass


def dbus_method_async(*args, **kwargs) -> Any:
    def decorator(f: Any) -> Any:
        return f

    return decorator


def dbus_signal_async(*args, **kwargs) -> Any:
    def decorator(f: Any) -> Any:
        return Signal()

    return decorator


class DbusInterfaceCommonAsync:
    def __init_subclass__(cls: Type[Self], *args, **kwargs) -> None:
        pass

    def export_to_dbus(self: Self, path: str) -> None:
        pass


async def request_default_bus_name_async(bus_name: str) -> None:
    pass
