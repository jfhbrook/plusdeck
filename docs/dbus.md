# DBus Service and Client

The `plusdeck` library includes a DBus service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients (including `plusdeckctl`) can connect to the service.

For information on the API, visit [the API docs for `plusdeck.dbus`](./api/plusdeck.dbus.md).

## plusdeckd

The DBus service can be launched using `plusdeckd`:

```sh
$ plusdeckd --help
Usage: plusdeckd [OPTIONS]

  Expose the Plus Deck 2C PC Cassette Deck as a DBus service.

Options:
  -C, --config-file PATH          A path to a config file
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --help                          Show this message and exit.
```

In most cases, this can be called without arguments. By default, `plusdeckd` will use the global config file at `/etc/plusdeck.yml`.

## plusdeckctl

Assuming `plusdeckd` is running, you may interact with the service using `plusdeckctl`:

```sh
$ plusdeckctl --help
Usage: plusdeckctl [OPTIONS] COMMAND [ARGS]...

  Control your Plus Deck 2C Cassette Drive through dbus.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --output [text|json]            Output either human-friendly text or JSON
  --help                          Show this message and exit.

Commands:
  config        Configure plusdeck.
  eject         Eject the tape
  expect        Wait for an expected state
  fast-forward  Fast-forward a tape
  pause         Pause the tape
  play          Play a tape
  rewind        Rewind a tape
  stop          Stop the tape
  subscribe     Subscribe to state changes
```

The interface is *very* similar to the vanilla `plusdeck` CLI. Note, however, that the config commands are slightly different. `plusdeckd` doesn't watch or reload the configuration in-place, so `plusdeckctl` will instead show the drift between the relevant config file and the loaded configuration. To synchronize the configuration, restart `plusdeckd` - if running under systemd, this will be `systemctl restart plusdeck` or similar.
