"""
This type stub file was generated by pyright.
"""

from typing import Any, AsyncContextManager, List, TYPE_CHECKING, TypeVar, Union
from unittest import IsolatedAsyncioTestCase
from .dbus_proxy_async_signal import DbusSignalAsyncBaseBind, DbusSignalAsyncLocalBind, DbusSignalAsyncProxyBind
from .sd_bus_internals import SdBus

if TYPE_CHECKING:
    T = TypeVar('T')
dbus_config = ...
class DbusSignalRecorderBase:
    def __init__(self, timeout: Union[int, float]) -> None:
        ...
    
    async def start(self) -> None:
        ...
    
    async def stop(self) -> None:
        ...
    
    async def __aenter__(self) -> DbusSignalRecorderBase:
        ...
    
    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        ...
    
    @property
    def output(self) -> List[Any]:
        ...
    


class DbusSignalRecorderRemote(DbusSignalRecorderBase):
    def __init__(self, timeout: Union[int, float], bus: SdBus, remote_signal: DbusSignalAsyncProxyBind[Any]) -> None:
        ...
    
    async def __aenter__(self) -> DbusSignalRecorderBase:
        ...
    
    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        ...
    


class DbusSignalRecorderLocal(DbusSignalRecorderBase):
    def __init__(self, timeout: Union[int, float], local_signal: DbusSignalAsyncLocalBind[Any]) -> None:
        ...
    
    async def __aenter__(self) -> DbusSignalRecorderBase:
        ...
    


class IsolatedDbusTestCase(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        ...
    
    async def asyncSetUp(self) -> None:
        ...
    
    def assertDbusSignalEmits(self, signal: DbusSignalAsyncBaseBind[Any], timeout: Union[int, float] = ...) -> AsyncContextManager[DbusSignalRecorderBase]:
        ...
    


