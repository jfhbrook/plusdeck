# DBus Client CLI

Assuming the DBus service is running, you may interact with the service using the client CLI:

```sh
$ python3 -m plusdeck.dbus.client --help
Usage: python3 -m plusdeck.dbus.client [OPTIONS] COMMAND [ARGS]...

  Control your Plus Deck 2C Cassette Drive through dbus.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --output [text|json]            Output either human-friendly text or JSON
  --user / --default              Connect to either the user or default bus
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

The interface is similar to the vanilla CLI. However, there are a few differences:

1. By default, the DBus client CLI will connect to the default bus. To connect to the user session bus, set the `--user` flag. To connect to the system bus, set the `--system` flag.
2. Configuration commands do not reload the service's configuration. Instead, they will update the relevant config file, and show the differences between the file config and the service's loaded config.
3. If the config file isn't owned by the user, the client CLI will attempt to run editing commands with `sudo`.

## Installing the `plusdeck-dbus` Shim

Included in this project is `./bin/plusdeck-dbus`, a script that you can add to your PATH for convenience. If you primarily interact with the device through DBus, you may want to name this `plusdeck` on your system.
