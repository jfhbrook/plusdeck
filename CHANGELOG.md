2025/02/04 Version 3.0.0
------------------------
- Remove `appdirs` dependency
- dbus support:
  - `plusdeck.dbus.DbusInterface` dbus Interface class
  - `plusdeck.dbus.DbusClient` dbus client class
  - `plusdeckd` dbus service CLI
  - `plusdeckctl` dbus client CLI
  - systemd unit for `plusdeckd`
- `python-plusdeck` COPR package spec
- `plusdeck` COPR package spec
  - Depends on `python-plusdeck` COPR package
  - Includes systemd unit for `plusdeckd`
- Tito based release tagging
- GitHub release tarball
- Improved documentation

2025/01/26 Version 2.0.0
------------------------
- Multiple APIs support an optional `timeout` argument
  - `client.wait_for`
  - `receiver.get_state`
  - `receiver.expect`
- CLI changes to support timeouts
  - `plusdeck` command no longer supports a global timeout
  - `plusdeck expect` supports an optional `--timeout` option
  - `plusdeck subscribe` supports a `--for` option that specifies how long to subscribe before exiting
- Bugfix in `receiver.expect` when processing multiple non-matching state changes

2025/01/26 Version 1.0.1
------------------------
- Fix `.readthedocs.yaml`
- Remove `pyyaml` dependency

2025/01/26 Version 1.0.0
------------------------
- Initial release
