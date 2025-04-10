# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
from typing import Dict, Generator, List, Optional
from unittest.mock import Mock

import pytest

from tests.helpers import Cli, EnvFactory

from plusdeck.client import Client, State
import plusdeck.config

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--system", action="store", default=False, help="Connect to the system bus"
    )


@pytest.fixture
async def client():
    client = Client()
    client._transport = Mock(name="client._transport")
    client.state = State.SUBSCRIBED
    return client


@pytest.fixture
def environment(monkeypatch, config_file: str, port: str) -> Dict[str, str]:
    environ = dict(PLUSDECK_CONFIG=config_file, PLUSDECK_PORT=port)
    monkeypatch.setattr(os, "environ", environ)
    return environ


@pytest.fixture
def config_file(monkeypatch) -> str:
    if "PLUSDECK_CONFIG_FILE" in os.environ:
        return os.environ["PLUSDECK_CONFIG_FILE"]

    path = Path(__file__).parent / "fixtures/crystalfontz.yaml"

    return str(path)


@pytest.fixture
def port(monkeypatch) -> str:
    port = "/dev/ttyUSB0"

    def default_port() -> str:
        return port

    monkeypatch.setattr(plusdeck.config, "default_port", default_port)

    return port


@pytest.fixture
def log_level() -> str:
    if "PLUSDECK_LOG_LEVEL" in os.environ:
        return os.environ["PLUSDECK_LOG_LEVEL"]
    return "INFO"


@pytest.fixture
def cli_env(config_file: str, port: str, log_level: str) -> EnvFactory:
    def factory(env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        _env: Dict[str, str] = dict(os.environ)

        if env:
            _env.update(env)

        _env["PLUSDECK_CONFIG_FILE"] = config_file
        _env["PLUSDECK_PORT"] = port
        _env["PLUSDECK_LOG_LEVEL"] = log_level

        return _env

    return factory


@pytest.fixture
def cli(cli_env: EnvFactory) -> Cli:
    return Cli(["python3", "-m", "plusdeck"], env=cli_env())


@pytest.fixture
def dbus_service(
    cli_env: EnvFactory, request: pytest.FixtureRequest
) -> Generator[None, None, None]:
    cli = Cli(["python3", "-m", "plusdeck.dbus.service", "--user"], env=cli_env())

    if request.config.getoption("--system"):
        logger.info("Connecting to system bus")
        yield
        return

    with cli.bg():
        yield


@pytest.fixture
def dbus_cli(
    cli_env: EnvFactory, dbus_service: None, request: pytest.FixtureRequest
) -> Cli:
    argv: List[str] = [
        "python3",
        "-m",
        "plusdeck.dbus.client",
        "--system" if request.config.getoption("--system") else "--user",
    ]

    if not request.config.getoption("--system"):
        argv.append("--user")

    return Cli(argv, env=cli_env())
