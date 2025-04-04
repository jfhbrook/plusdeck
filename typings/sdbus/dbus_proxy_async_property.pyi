"""
This type stub file was generated by pyright.
"""

from typing import Any, Awaitable, Callable, Generator, Generic, Optional, TYPE_CHECKING, Type, TypeVar, Union, overload
from .dbus_common_elements import DbusBindedAsync, DbusPropertyCommon, DbusRemoteObjectMeta, DbusSomethingAsync
from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync

if TYPE_CHECKING:
    ...
T = TypeVar('T')
class DbusPropertyAsync(DbusSomethingAsync, DbusPropertyCommon, Generic[T]):
    def __init__(self, property_name: Optional[str], property_signature: str, property_getter: Callable[[DbusInterfaceBaseAsync], T], property_setter: Optional[Callable[[DbusInterfaceBaseAsync, T], None]], flags: int) -> None:
        ...
    
    @overload
    def __get__(self, obj: None, obj_class: Type[DbusInterfaceBaseAsync]) -> DbusPropertyAsync[T]:
        ...
    
    @overload
    def __get__(self, obj: DbusInterfaceBaseAsync, obj_class: Type[DbusInterfaceBaseAsync]) -> DbusPropertyAsyncBaseBind[T]:
        ...
    
    def __get__(self, obj: Optional[DbusInterfaceBaseAsync], obj_class: Optional[Type[DbusInterfaceBaseAsync]] = ...) -> Union[DbusPropertyAsyncBaseBind[T], DbusPropertyAsync[T]]:
        ...
    
    def setter(self, new_set_function: Callable[[Any, T], None]) -> None:
        ...
    
    def setter_private(self, new_set_function: Callable[[Any, T], None]) -> None:
        ...
    


class DbusPropertyAsyncBaseBind(DbusBindedAsync, Awaitable[T]):
    def __await__(self) -> Generator[Any, None, T]:
        ...
    
    async def get_async(self) -> T:
        ...
    
    async def set_async(self, complete_object: T) -> None:
        ...
    


class DbusPropertyAsyncProxyBind(DbusPropertyAsyncBaseBind[T]):
    def __init__(self, dbus_property: DbusPropertyAsync[T], proxy_meta: DbusRemoteObjectMeta) -> None:
        ...
    
    async def get_async(self) -> T:
        ...
    
    async def set_async(self, complete_object: T) -> None:
        ...
    


class DbusPropertyAsyncLocalBind(DbusPropertyAsyncBaseBind[T]):
    def __init__(self, dbus_property: DbusPropertyAsync[T], local_object: DbusInterfaceBaseAsync) -> None:
        ...
    
    async def get_async(self) -> T:
        ...
    
    async def set_async(self, complete_object: T) -> None:
        ...
    


def dbus_property_async(property_signature: str = ..., flags: int = ..., property_name: Optional[str] = ...) -> Callable[[Callable[[Any], T]], DbusPropertyAsync[T]]:
    ...

def dbus_property_async_override() -> Callable[[Callable[[Any], T]], DbusPropertyAsync[T]]:
    ...

