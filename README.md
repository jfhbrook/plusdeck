# Plus Deck 2C PC Cassette Deck

The Plus Deck 2C is a cassette deck that mounts in a 5.25" PC drive bay and is controlled over RS-232 serial. It was intended for archiving cassette tapes to mp3 - note that it can not *write* to cassettes. Here's the Amazon page for it:

<https://www.amazon.com/Plusdeck-2c-PC-Cassette-Deck/dp/B000CSGIJW>

It was initally released in the 2000s, and they are currently difficult to find. However, I always wanted one as a teenager and, as an adult, bought one for Too Much Money, and am currently writing modern tools for using it in a modern PC.

This project contains a Python library for interacting with the Plus Deck 2C
over serial, using `asyncio`.

## Install

`plusdeck` is a Python package, and therefore can be installed [from PyPi](https://pypi.org/project/plusdeck/), for instance with `pip`:

```sh
pip install plusdeck
```

In addition, I have a Fedora package on COPR, which can be installed like so:

```sh
sudo dnf copr enable jfhbrook/joshiverse
sudo dnf install plusdeck
```

## Usage

Here's a basic example:

```py
import asyncio

from plusdeck import connection


async def main():
    # Will close the client on exit
    async with connection("/dev/ttyS0") as client:
        # Play the tape
        client.play_a()

asyncio.run(main())
```

This will play the tape on side A, assuming it has been inserted into the Plus Deck.

The client has methods for every other command supported by the Plus Deck 2C as well:

| method           | behavior                                             |
|------------------|------------------------------------------------------|
| `play_a`         | Play side A                                          |
| `play_b`         | Play side B                                          |
| `fast_forward_a` | Fast-forward side A (equivalent to rewinding side B) |
| `fast_forward_b` | Fast-forward side B (equivalent to rewinding side A) |
| `rewind_a`       | Rewind side A (equivalent to fast-forwarding side B) |
| `rewind_b`       | Rewind side B (equivalent to fast-forwarding side A) |
| `pause`          | Pause or unpause playback                            |
| `stop`           | Stop the tape                                        |
| `eject`          | Eject the tape                                       |

### Subscribing to State Changes

The Plus Deck 2C will, if commanded to do so, emit its state on an interval. The client will deduplicate these states and emit changes as events. The most idiomatic way to interact with these events is to use the `session` method to access a `Receiver`, which allows for both "expecting" a state change and iterating over changes in state. The "expect" API looks like this:

```py
import asyncio

from plusdeck import connection, State


async def main():
    async with connection("/dev/ttyS0") as client:
        # Access a receiver - will unsubscribe when the context manager exits
        async with client.session() as rcv:
            # Wait for the tape to eject
            await rcv.expect(State.EJECTED)

asyncio.run(main())
```

Iterating over state changes looks like this:

```py
import asyncio

from plusdeck import connection


async def main():
    async with connection("/dev/ttyS0") as client:
        async with client.session() as rcv:
            # Print out every state change
            async for state in rcv:
                print(state)

asyncio.run(main())
```

Note that, by default, these APIs will wait indefinitely for an event to occur. This is because commands sent by the client are generally assumed to succeed, and "expected" state changes are typically triggered by a human being through the Plus Deck 2C's physical interface. That said, `expect` accepts a `timeout` parameter:

```py
await rcv.expect(State.PLAY_A, timeout=1.0)
```

If you want to iterate over general events with a timeout - for instance, if you need to unblock to execute some other action on a minimal interval - you may use the lower level `get_state` API:

```py
state: State = await rcv.get_state(timeout=1.0)
```

## CLI

This library has a CLI, which you can run like so:

```sh
$ plusdeck --help
Usage: plusdeck [OPTIONS] COMMAND [ARGS]...

  Control your Plus Deck 2C tape deck.

Options:
  --global / --no-global          Load the global config file at
                                  /etc/plusdeck.yaml (default true when called
                                  with sudo)
  -C, --config-file PATH          A path to a config file
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --port TEXT                     The serial port the device is connected to
  --output [text|json]            Output either human-friendly text or JSON
  --timeout FLOAT                 How long to wait for a response from the
                                  device before timing out
  --help                          Show this message and exit.

Commands:
  config        Configure plusdeck.
  eject         Eject the tape
  expect        Wait for an expected state
  fast-forward  Fast-forward a tape
  pause         Pause the tape
  play          Play a tape
  rewind        Rewind a tape
  stop          Stop the tape
  subscribe     Subscribe to state changes
```

## Jupyter Widgets

This library also includes some simple Jupyter widgets, under the `plusdeck.jupyter` namespace. These are `ConfigEditor`, for editing the CLI configuration file, and `player`, for spawning a simple player UI. To see these in action, check out the `Player.ipynb` file in the root of this project.

## Development

I use `uv` for managing dependencies, but also compile `requirements.txt` and `requirements_dev.txt` files that one can use instead. I also use `just` for task running, but if you don't have it installed you can run the commands manually.

This library has somewhat comprehensive unit test coverage through `pytest`. Additionally, it has an interactive integration test suite, using a bespoke test framework, which can be run with `just integration`.

## Documentation

Other documentation is in [./docs](./docs).

## Changelog

See [`CHANGELOG.md`](./CHANGELOG.md).

## License

MIT, see [`LICENSE`](./LICENSE).
