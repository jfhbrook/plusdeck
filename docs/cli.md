# Command Line Interface

The `plusdeck` CLI allows for direct control of the Plus Deck 2C over its serial port:

```sh
$ plusdeck --help
Usage: plusdeck [OPTIONS] COMMAND [ARGS]...

  Control your Plus Deck 2C tape deck.

Options:
  --global / --no-global          Load the global config file at
                                  /etc/plusdeck.yaml (default true when called
                                  with sudo)
  -C, --config-file PATH          A path to a config file
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --port TEXT                     The serial port the device is connected to
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

For more information, use the `--help` flag for any command.
