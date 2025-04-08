# -*- coding: utf-8 -*-

from contextlib import contextmanager
import os
import subprocess
from typing import Dict, Generator, List, Optional, Protocol, Self

from crystalfontz.character import SpecialCharacter


class Cli:
    """
    A fixture for running CLI commands
    """

    def __init__(
        self: Self,
        argv: List[str],
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.argv: List[str] = argv
        self.env: Dict[str, str] = env or dict(os.environ)

    def __call__(self: Self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            self.argv + list(argv),
            capture_output=True,
            check=True,
            env=self.env,
        )

    @contextmanager
    def bg(self: Self, *argv: str, quiet: bool = True) -> Generator[None, None, None]:
        proc = subprocess.Popen(
            self.argv + list(argv),
            stderr=subprocess.DEVNULL if quiet else None,
            env=self.env,
        )

        yield

        proc.terminate()


class EnvFactory(Protocol):
    def __call__(
        self: Self, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]: ...


def special_character_as_rows(character: SpecialCharacter) -> List[str]:
    return ["".join(["█" if p else " " for p in row]) for row in character.pixels]
