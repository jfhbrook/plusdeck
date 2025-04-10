# Install

`plusdeck` is released as a PyPI package, a series of COPR packages, and a GitHub release.

## Python Package

`plusdeck` is a Python package, and therefore can be installed [from PyPi](https://pypi.org/project/plusdeck/), for instance with `pip`:

```sh
pip install plusdeck
```

This package contains the Python library, with the CLIs exposed with Python's `-m` flag (ie. `python3 -m plusdeck`).

## COPR Packages

I package `plusdeck` for Fedora on COPR. It can be installed like so:

```sh
sudo dnf copr enable jfhbrook/joshiverse
sudo dnf install plusdeck
```

This package installs the Python package via `python-plusdeck`, configures the systemd service, and includes a bin called `plusdeck` that wraps `python3 -m plusdeck.dbus.client`.

## GitHub Release

`plusdeck` is also published as a GitHub release:

<https://github.com/jfhbrook/plusdeck/releases>

These releases simply contain packaged source code, and will mostly be useful for package authors.
