import asyncio
from inspect import getmembers, isfunction
import sys
from typing import Callable, Set, TypeVar

from rich.prompt import Prompt

from plusdeck import Command, create_connection, State

PORT = "/dev/ttyUSB0"


class AbortError(Exception):
    pass


def manual_confirm(text: str) -> None:
    res = Prompt.ask(text, choices=["confirm", "abort"])

    if res == "abort":
        raise AbortError("Aborted.")


def manual_action(text: str) -> None:
    res = Prompt.ask(text, choices=["continue", "abort"])

    if res == "abort":
        raise AbortError("Aborted.")


def manual_test(text: str) -> bool:
    res = Prompt.ask(text, choices=["yes", "no", "abort"])

    if res == "abort":
        raise AbortError("Aborted.")

    return res == "yes"


SKIP: Set[str] = set()

Test = TypeVar(name="Test", bound=Callable)


def skip(fn: Test) -> Test:
    SKIP.add(fn.__name__)
    return fn


@skip
async def test_manual_no_events():
    """Plus Deck plays tapes manually without state subscription."""

    manual_confirm("There is NO tape in the deck")

    client = await create_connection(PORT)

    @client.events.on("state")
    def unexpected_state(state: State):
        assert not state, "Should not receive state before enabling"

    manual_action("Put a tape in the deck")
    assert manual_test("Press Rewind. Has the tape rewound?"), "Deck rewound"
    assert manual_test(
        "Press Play Side A. Is the deck playing side A?"
    ), "Deck is playing side A"
    assert manual_test("Press Pause. Is the tape paused?"), "Deck is paused"
    assert manual_test("Press Pause. Is the tape playing?"), "Deck is playing"
    assert manual_test(
        "Press Fast-Forward. Has the tape fast-forwarded?"
    ), "Deck fast-forwarded"
    assert manual_test(
        "Press Play Side B. Is the deck playing side B?"
    ), "Deck is playing side B"
    assert manual_test("Press Stop. Has the tape has stopped playing?")
    assert manual_test("Press Eject. Did the tape eject?"), "Deck has ejected"

    client.events.remove_listener("state", unexpected_state)

    client.close()


async def test_commands_and_events():
    """Plus Deck plays tapes with commands when subscribed."""

    manual_confirm("There is NO tape in the deck")

    client = await create_connection(PORT)

    @client.events.on("state")
    def log_state(state: State) -> None:
        print(f"# {state}")

    async with client.session():
        w1 = client.wait_for(State.Stopped)

        manual_action("Put a tape in the deck")

        await w1

        w2 = client.wait_for(State.Rewinding)

        client.send(Command.Rewind)

        await w2

        await client.wait_for(State.Stopped)

        w3 = client.wait_for(State.PlayingA)

        client.send(Command.PlayA)

        await w3

        assert manual_test(
            "Did the deck rewind and start playing side A?"
        ), "Deck is playing side A"

        w4 = client.wait_for(State.PausedA)

        client.send(Command.Pause)

        await w4

        assert manual_test("Did the deck pause?"), "Deck is paused on side A"

        w5 = client.wait_for(State.PlayingA)

        client.send(Command.Pause)

        await w5

        assert manual_test(
            "Did the deck start playing side A again?"
        ), "Deck is playing side A"

        w6 = client.wait_for(State.FastForwarding)

        client.send(Command.FastForward)

        await w6

        await client.wait_for(State.Stopped)

        w7 = client.wait_for(State.PlayingB)

        client.send(Command.PlayB)

        await w7

        assert manual_test(
            "Did the deck fast-forward and start playing side B?"
        ), "Deck is playing side B"

        w8 = client.wait_for(State.PausedB)

        client.send(Command.Pause)

        await w8

        assert manual_test("Did the deck pause?"), "Deck is paused on side A"

        w9 = client.wait_for(State.PlayingB)

        client.send(Command.Pause)

        await w9

        assert manual_test(
            "Did the deck start playing side B again?"
        ), "Deck is playing side B"

        w10 = client.wait_for(State.Ejected)

        client.send(Command.Eject)

        await w10

        assert manual_test("Did the deck eject the tape?"), "Deck has ejected"

    client.events.remove_listener("state", log_state)

    client.close()


async def run_tests():
    for name, fn in getmembers(sys.modules[__name__], isfunction):
        if not name.startswith("test_"):
            continue

        if name in SKIP:
            print(f"=== {name} SKIPPED ===")
            continue

        print(f"=== {name} ===")
        try:
            coro = fn()
            if asyncio.iscoroutine(coro):
                await coro
        except Exception as exc:
            print(f"{name} FAILED")
            print(exc)
        else:
            print(f"=== {name} PASSED ===")


loop = asyncio.get_event_loop()

loop.run_until_complete(run_tests())
