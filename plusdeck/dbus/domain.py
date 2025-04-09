from typing import Any, cast, ClassVar, Optional, Protocol, Self, Tuple, Type, Union

from plusdeck.client import State
from plusdeck.config import Config


class TypeProtocol(Protocol):
    t: ClassVar[str]


def t(*args: Union[str, Type[TypeProtocol]]) -> str:
    type_ = ""

    for arg in args:
        if isinstance(arg, str):
            type_ += arg
        else:
            type_ += arg.t

    return type_


def struct(*args: Union[str, Type[TypeProtocol]]) -> str:
    return t("(", *args, ")")


OptFloatT = float


class OptFloatM:
    """
    Map `Optional[float]` to and from `OptFloatT` (`float`), where float values
    are expected to be positive.

    None values are represented by negative values, namely `-1.0`.
    """

    t: ClassVar[str] = "d"
    none: ClassVar[OptFloatT] = -1.0

    @classmethod
    def pack(cls: Type[Self], t: Optional[float]) -> OptFloatT:
        """
        Pack `Optional[float]` to `OptFloatT`.
        """

        return t if t is not None else cls.none

    @staticmethod
    def unpack(t: OptFloatT) -> Optional[float]:
        """
        Unpack `OptFloatT` to `Optional[float]`.
        """

        return t if t >= 0 else None


OptStrT = str


class OptStrM:
    """
    Map `Optional[str]` to and from `StrT` (`str`).

    None values are represented by an empty string.
    """

    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], string: Optional[str]) -> OptStrT:
        """
        Pack `Optional[str]` to `OptStrT`.
        """

        return string or cls.none

    @classmethod
    def unpack(cls: Type[Self], string: OptStrT) -> Optional[str]:
        """
        Unpack `OptStrT` to `Optional[str]`.
        """

        return string if string != cls.none else None


TimeoutT = float


class TimeoutM(OptFloatM):
    """
    Map `Optional[float]` to and from `TimeoutT` (`float`).

    `TimeoutM` is an alias for `OptFloatM`.
    """

    t: ClassVar[str] = OptFloatM.t
    none: ClassVar[float] = OptFloatM.none


FileT = OptStrT


class FileM(OptStrM):
    t: ClassVar[str] = OptStrM.t
    none: ClassVar[str] = OptStrM.none


PortT = str


class PortM:
    t: ClassVar[str] = "s"


ConfigT = Tuple[FileT, PortT]


class ConfigM:
    """
    Map `Config` to and from `ConfigT`
    (`Tuple[Optional[str], str]`).
    """

    t: ClassVar[str] = struct(FileM, PortM)

    @staticmethod
    def pack(config: Config) -> ConfigT:
        """
        Pack `Config` to `ConfigT`.
        """

        return (FileM.pack(config.file), config.port)

    @staticmethod
    def unpack(config: ConfigT) -> Config:
        """
        Unpack `ConfigT` to `Config`.
        """

        file, port = config

        return cast(Any, Config)(file=file, port=port)


StateT = str


class StateM:
    """
    Map `State` to and from `StateT` (`str`).
    """

    t: ClassVar[str] = "s"

    @staticmethod
    def pack(state: State) -> StateT:
        return state.name

    @staticmethod
    def unpack(state: StateT) -> State:
        return State[state]
