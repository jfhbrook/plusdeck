from typing import Any, List, Optional

try:
    from typing import Self
except ImportError:
    Self = Any

import click

from plusdeck.client import State

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
