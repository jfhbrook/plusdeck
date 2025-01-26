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
