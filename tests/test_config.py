from plusdeck.config import Config


def test_from_environment(environment, port):
    """Loads config from the environment"""

    assert Config.from_environment() == Config(
        file=None, port=environment["PLUSDECK_PORT"]
    )


def test_from_file_no_environment(environment, config_file, port):
    """Loads config from a file."""

    assert Config.from_file(config_file) == Config(
        file=config_file, port="/dev/ttyUSB2"
    )


def test_from_file_and_environment(environment, config_file, port):
    """Loads config from a file with environment overrides."""

    assert Config.from_file(load_environment=True) == Config(
        file=config_file, port=environment["PLUSDECK_PORT"]
    )
