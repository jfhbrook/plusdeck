# DBus Support

The `plusdeck` library includes a DBus interface, service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients (including `plusdeckctl`) can connect to the service.

For information on the API, visit [the API docs for `plusdeck.dbus`](../api/plusdeck.dbus.md).
