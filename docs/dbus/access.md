# Dbus Access Policies

When running services under the `system` bus, care must be taken to manage access policies. Dbus does this primarily with [an XML-based policy language](https://dbus.freedesktop.org/doc/dbus-daemon.1.html). Systemd additionally manages access to privileged methods, seemingly with the intent of delegating to polkit.

By default, Dbus is configured with the following policies:

* The root user may own the bus, and send and receive messages from `org.jfhbrook.plusdeck`
* Users in the `plusdeck` Unix group may additionally send and receive messages from `org.jfhbrook.plusdeck`

This means that, if the service is running, `sudo plusdeckctl` commands should always work; and that if your user is in the `plusdeck` Unix group, Dbus will allow for unprivileged `plusdeckctl` commands as well. You can create this group and add yourself to it by running:

```bash
sudo groupadd plusdeck
sudo usermod -a -G plusdeck "${USER}"
```
