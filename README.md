# Plus Deck 2C PC Cassette Deck

The Plus Deck 2C is a cassette deck that mounts in a 5.25" PC drive bay and is controlled over RS-232 serial. It was intended for archiving cassette tapes to mp3 - note that it can not *write* to cassettes. Here's the Amazon page for it:

<https://www.amazon.com/Plusdeck-2c-PC-Cassette-Deck/dp/B000CSGIJW>

It was initally released in the 2000s, and they are currently difficult to find. However, I always wanted one as a teenager and, as an adult, bought one for Too Much Money, and am currently writing modern tools for using it in a modern PC.

This project contains a Python library for interacting with the Plus Deck 2c
over serial, using `asyncio`.

### Developer Setup

To work with this project, you will need a working `python3` and `npm`, and
[just](https://github.com/casey/just) will need to be installed. You will also
need a Plus Deck.

A full list of commands can be seen by running `just list`. But the big ones
are:

```bash
# Install dependencies
just install

# Run type checking and tests, then format and lint
just

# Check types
just check

# Test
just test

# Format
just format

# Lint
just lint

# Run jupterlab for interactive testing
just jupyterlab
```

## Documentation

Other documentation is in [./docs](./docs).

## Changelog

See `CHANGELOG.md`.

## License

MIT, see ``LICENSE``.
