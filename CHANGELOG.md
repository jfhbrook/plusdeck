yyyy/mm/dd Version x.y.z-1
------------------------
- Include generated DBus interface docs
- Fix links in documentation
- CLI respects `CRYSTALFONTZ_CONFIG_FILE` environment variable
- Remove `tox` from development tools
- Consistently licensed as MPL-2.0
- Improved PyPI classifiers

2025/02/09 Version 4.0.1-1
--------------------------
- Dbus methods now marked as unprivileged
- sdbus library errors have improved logging

2025/02/06 Version 4.0.0-1
--------------------------
- `plusdeckctl` connects to the system bus by default
- `plusdeckctl --user` will connect to the user bus
- `plusdeckd` loads local config by default unless run as root
- systemd unit fixes
  - Requires `dbus.socket`, starts after `dbus.socket`
  - Wanted by `multiuser.target`
- dbus access policy
  - Ownership and allowed destination for root
  - Allowed destination for `plusdeck` user

2025/02/04 Version 3.0.0-3
--------------------------
- Fix install path of systemd unit

2025/02/04 Version 3.0.0-1
--------------------------
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
