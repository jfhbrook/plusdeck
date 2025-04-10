# plusdeck.dbus.domain

DBus uses a collection of types that are documented [in the specification](https://dbus.freedesktop.org/doc/dbus-specification.html#basic-types). The base types are more fine-grained than Python's base types, but are non-nullable - ie, there's no `None` type in DBus. Moreover, its collection types don't map cleanly to arbitrary Python class instances - rather, you get basic structs (which correspond to Python tuples) and arrays (which correspond to Python lists). This means that, when interacting with the DBus client, you will need to work with types *other* than the domain objects used in the standard `plusdeck` client.

To facilitate this, `plusdeck` includes a submodule for mapping between domain objects and DBus types, at `plusdeck.dbus.domain`. This module exports both aliases for the types used by the DBus interface, and mapper classes for packing and unpacking domain objects to and from DBus types.

::: plusdeck.dbus.domain
