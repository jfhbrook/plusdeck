# Dialout

In Linux, by default, accessing serial ports requires `sudo`. This is inconvenient - you probably want your current user to have acccess without using `sudo`.

Typically, Linux serial ports are generally owned by `root` and are attached to the `dialout` group, with permissions such that members of the `dialout` group may read and write to the port.

To add your user to the `dialout` group, you can run a command like this:

```bash
usermod -a -G dialout "${USER}"
```

Note that you may need to log out and back in before this takes effect.
