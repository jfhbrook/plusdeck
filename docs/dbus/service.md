# DBus Service

`plusdeck` includes a dbus service, which can be started with the `plusdeckctl` CLI tool.

## Starting the Service

`plusdeck` ships with a systemd unit that configures the service as a Dbus service. To set up the service, run:

```sh
sudo systemctl enable plusdeck
sudo systemctl start plusdeck  # optional
```

This unit will start on the `system` bus, under the root user.

## Running `plusdeckd` Directly

The DBus service can be launched directly using `plusdeckd`:

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

In most cases, this can be called without arguments. By default, `plusdeckd` will listen on the `system` bus and load the global config file (`/etc/plusdeck.yml`) if launched as root; and otherwise listen on the `user` bus and load the user's config file (`~/.config/plusdeck.yml`).
