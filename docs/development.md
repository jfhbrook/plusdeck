# Development

## Dependencies

### Development

- [just](https://github.com/casey/just)
  - Alternatively, can run commands manually
- [uv](https://github.com/astral-sh/uv)
  - Alternatively, can use `requirements_dev.txt` and run commands manually
- [shellcheck](https://github.com/koalaman/shellcheck)
- [npx](https://docs.npmjs.com/cli/v8/commands/npx/) for running `pyright`

### Publishing

- COPR tools
  - [coprctl](https://github.com/jfhbrook/public/tree/main/coprctl)
    - MacOS: `brew install jfhbrook/joshiverse/coprctl`
  - [tito](https://github.com/rpm-software-management/tito)
    - MacOS: `brew install jfhbrook/joshiverse/tito`
  - [COPR CLI](https://developer.fedoraproject.org/deployment/copr/copr-cli.html)
    - MacOS: `brew install jfhbrook/joshiverse/copr`
  - MacOS: [Docker](https://www.docker.com/)
- [yq](https://github.com/mikefarah/yq)
- [gomplate](https://github.com/hairyhenderson/gomplate)
- `op` CLI, with a secret called `PyPI` and a field called `API Token` with an API token in it

## Common Tasks

### Setup

- `install` - Install dependencies
- `update` - Update all dependencies
- `upgrade` - Update all dependencies and rebuild the environment

### Quality Assurance

- `default` - Format, run checks and tests, and lint
- `format` - Format Python files with `black`
- `check` - Check types with `pyright`
- `test` - Run unit tests
- `snap` - Update snapshots for unit tests
- `integration` - Run integration tests (need a real Plus Deck 2C)
- `lint` - Lint the project

### Interactive

- `run` - Thin wrapper around `uv run`
- `client` - Run `plusdeck` serial client CLI
- `service` - Run `plusdeck.dbus.service` DBus service on user session bus
- `dbus-client` - Run `plusdeck.dbus.client` DBus client CLI on user session bus
- `console` - Run a Python repl
- `shell` - Start a bash shell with a sourced virtualenv

### Other

- `compile` - Compile `requirements.txt` and `requirements_dev.txt`
- `docs` - Serve the mkdocs documentation
- `publish` - Run all publish tasks

## Integration Tests

You can run integration tests with `just integration`. It optionally takes arguments. You can show them with `just integration --help`:

```
./scripts/integration.sh --help
USAGE: ./scripts/integration.sh [OPTIONS] [COMPONENTS]

Run integration tests for the supplied components. By default, runs client tests.

Components:
    client  Run plusdeck client integration tests
    dbus    Start plusdeck dbus integration tests

Options:
    --help             Show this help text
    --snapshot-update  Update snapshots
    --system           Run any dbus tests against the system bus

    Other options are passed to pytest.

Environment:
    PLUSDECK_CONFIG_FILE  Use an alternative config file. The default is
                              ./tests/fixtures/plusdeck.yaml.
    PLUSDECK_LOG_LEVEL    
```

To run standard client tests, you can do `just integration`. For DBus tests, do `just integration dbus`.

## CHANGELOG.md

When submitting features, be sure to update the changelog!
