import asyncio

from rich.prompt import Confirm, Prompt

from plusdeck import Command, State, create_connection

PORT = '/dev/ttyUSB0'


class AbortError(Exception):
    pass


def confirm(text: str) -> None:
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


async def main():
    confirm("There is NO tape in the deck")

    client = await create_connection(PORT)

    @client.events.on("state")
    def unexpected_state(state: State):
        assert not state, "Should not receive state before enabling"

    manual_action("Put a tape in the deck")
    assert manual_test("Press Rewind. Has the tape rewound?"), "Deck rewound"
    assert manual_test("Press Play Side A. Is the deck playing side A?"), "Deck is playing side A"
    assert manual_test("Press Pause. Is the tape paused?"), "Deck is paused"
    assert manual_test("Press Pause. Is the tape playing?"), "Deck is playing"
    assert manual_test("Press Fast-Forward. Has the tape fast-forwarded?"), "Deck fast-forwarded"
    assert manual_test("Press Play Side B. Is the deck playing side B?"), "Deck is playing side B"
    assert manual_test("Press Stop. Has the tape has stopped playing?")
    assert manual_test("Press Eject. Did the tape eject?"), "Deck has ejected"


loop = asyncio.get_event_loop()

loop.run_until_complete(main())
