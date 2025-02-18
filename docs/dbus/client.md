# DBus Client CLI

Assuming `plusdeckd` is running, you may interact with the service using `plusdeckctl`:

```sh
$ plusdeckctl --help
Usage: plusdeckctl [OPTIONS] COMMAND [ARGS]...

  Control your Plus Deck 2C Cassette Drive through dbus.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --output [text|json]            Output either human-friendly text or JSON
  --user / --no-user              Connect to the user bus
  --help                          Show this message and exit.

Commands:
  config        Configure plusdeck.
  eject         Eject the tape
  expect        Wait for an expected state
  fast-forward  Fast-forward a tape
  pause         Pause the tape
  play          Play a tape
  rewind        Rewind a tape
  state         Get the current state
  stop          Stop the tape
  subscribe     Subscribe to state changes
```

The interface is similar to the vanilla `plusdeck` CLI. However, there are a few differences:

1. By default, `plusdeckctl` will connect to the `system` bus. To connect to the local bus, set the `--user` flag.
2. Configuration commands do not reload `plusdeckctl`'s configuration. Instead, they will update the relevant config file, and show the differences between the file config and the service's loaded config.
3. If the config file isn't owned by the user, `plusdeckctl` will attempt to run editing commands with `sudo`.
