# DBus Service and Client

The `plusdeck` library includes a DBus service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients (including `plusdeckctl`) can connect to the service.

For information on the API, visit [the API docs for `plusdeck.dbus`](./api/plusdeck.dbus.md).

## Starting the Dbus Service

`plusdeck` ships with a systemd unit that configures the service as a Dbus service. To set up the service, run:

```sh
sudo systemctl enable plusdeck
sudo systemctl start plusdeck  # optional
```

This unit will start on the `system` bus, under the root user.

## Running `plusdeckctl`

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

## Dbus Access Policies

When running services under the `system` bus, care must be taken to manage access policies. Dbus does this primarily with [an XML-based policy language](https://dbus.freedesktop.org/doc/dbus-daemon.1.html). Systemd additionally manages access to privileged methods, seemingly with the intent of delegating to polkit.

By default, Dbus is configured with the following policies:

* The root user may own the bus, and send and receive messages from `org.jfhbrook.plusdeck`
* Users in the `plusdeck` Unix group may additionally send and receive messages from `org.jfhbrook.plusdeck`

This means that, if the service is running, `sudo plusdeckctl` commands should always work; and that if your user is in the `plusdeck` Unix group, Dbus will allow for unprivileged `plusdeckctl` commands as well. You can create this group and add yourself to it by running:

```bash
sudo groupadd plusdeck
sudo usermod -a -G plusdeck "${USER}"
```

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

## Debugging Dbus

### Default Dbus Configuration

The default Dbus configuration is at `/usr/share/dbus-1/system.conf`. It may be useful to refer to this file when trying to understand what default access policies are being applied.

### Monitoring Dbus

The best tool for debugging Dbus seems to be [dbus-monitor](https://dbus.freedesktop.org/doc/dbus-monitor.1.html). To follow system bus messages, run:

```sh
sudo dbus-monitor --system
```

### Viewing Dbus Logs

You can review recent logs by checking the status of the `dbus` unit:

```sh
sudo systemctl status dbus
```

### Viewing the Dbus Interface

I have a just task for that:

```sh
just get-dbus-iface
```
