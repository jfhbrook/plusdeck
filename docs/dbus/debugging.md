# Debugging Dbus

## Default Dbus Configuration

The default Dbus configuration is at `/usr/share/dbus-1/system.conf`. It may be useful to refer to this file when trying to understand what default access policies are being applied.

## Monitoring Dbus

The best tool for debugging Dbus seems to be [dbus-monitor](https://dbus.freedesktop.org/doc/dbus-monitor.1.html). To follow system bus messages, run:

```sh
sudo dbus-monitor --system
```

## Viewing Dbus Logs

You can review recent logs by checking the status of the `dbus` unit:

```sh
sudo systemctl status dbus
```

## Printing the Live Dbus Interface

I have a just task for that:

```sh
just print-iface
```
