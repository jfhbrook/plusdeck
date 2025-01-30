"""
This type stub file was generated by pyright.
"""

from argparse import Action, ArgumentParser
from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
from .interface_generator import DbusInterfaceIntrospection

if TYPE_CHECKING:
    ...
@dataclass
class RenameMember:
    new_name: Optional[str] = ...
    current_arg: Optional[str] = ...
    arg_renames: Dict[str, str] = ...


@dataclass
class RenameInterface:
    new_name: Optional[str] = ...
    current_member: Optional[RenameMember] = ...
    methods: Dict[str, RenameMember] = ...
    properties: Dict[str, RenameMember] = ...
    signals: Dict[str, RenameMember] = ...


@dataclass
class RenameRoot:
    current_interface: Optional[RenameInterface] = ...
    interfaces: Dict[str, RenameInterface] = ...


rename_root = ...
def rename_members(interface: DbusInterfaceIntrospection, interface_rename: RenameInterface) -> None:
    ...

def rename_interfaces(interfaces: List[DbusInterfaceIntrospection]) -> None:
    ...

def run_gen_from_connection(connection_name: str, object_paths: List[str], system: bool, imports_header: bool, do_async: bool) -> None:
    ...

def run_gen_from_file(filenames: List[str], imports_header: bool, do_async: bool) -> None:
    ...

class ActionSelectInterface(Action):
    def __call__(self, parser: ArgumentParser, namespace: object, values: object, option_string: Optional[str] = ...) -> None:
        ...
    


class ActionSelectMethod(Action):
    def __call__(self, parser: ArgumentParser, namespace: object, values: object, option_string: Optional[str] = ...) -> None:
        ...
    


class ActionSelectProperty(Action):
    def __call__(self, parser: ArgumentParser, namespace: object, values: object, option_string: Optional[str] = ...) -> None:
        ...
    


class ActionSelectSignal(Action):
    def __call__(self, parser: ArgumentParser, namespace: object, values: object, option_string: Optional[str] = ...) -> None:
        ...
    


class ActionSetName(Action):
    def __call__(self, parser: ArgumentParser, namespace: object, values: object, option_string: Optional[str] = ...) -> None:
        ...
    


def generator_main(args: Optional[List[str]] = ...) -> None:
    ...

if __name__ == "__main__":
    ...
