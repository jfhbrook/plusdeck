# Getting Started

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

This will play the tape on side A, assuming it has been inserted into the Plus Deck 2C.

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

## Subscribing to State Changes

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
