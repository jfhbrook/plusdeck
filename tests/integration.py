from plusdeck.client import Command, create_connection, State
from plusdeck.test import check, confirm, run_tests, skip, take_action

PORT = "/dev/ttyUSB0"


@skip
async def test_manual_no_events():
    """Plus Deck plays tapes manually without state subscription."""

    confirm("There is NO tape in the deck")

    client = await create_connection(PORT)

    @client.events.on("state")
    def unexpected_state(state: State):
        assert not state, "Should not receive state before enabling"

    take_action("Put a tape in the deck")

    check("Press Rewind. Has the tape rewound?", "Deck rewound")
    check("Press Play Side A. Is the deck playing side A?", "Deck is playing side A")
    check("Press Pause. Is the tape paused?", "Deck is paused")
    check("Press Pause. Is the tape playing?", "Deck is playing")
    check("Press Fast-Forward. Has the tape fast-forwarded?", "Deck fast-forwarded")
    check("Press Play Side B. Is the deck playing side B?", "Deck is playing side B")
    check("Press Stop. Has the tape has stopped playing?", "Deck is stopped")
    check("Press Eject. Did the tape eject?", "Deck has ejected")

    client.events.remove_listener("state", unexpected_state)

    client.close()


async def test_commands_and_events():
    """Plus Deck plays tapes with commands when subscribed."""

    confirm("There is NO tape in the deck")

    client = await create_connection(PORT)

    @client.events.on("state")
    def log_state(state: State) -> None:
        print(f"# {state}")

    async with client.session() as rcv:
        take_action("Put a tape in the deck")

        await rcv.expect(State.Stopped)

        client.send(Command.Rewind)

        await rcv.expect(State.Rewinding)
        await rcv.expect(State.Stopped)

        client.send(Command.PlayA)

        await rcv.expect(State.PlayingA)

        check("Did the deck rewind and start playing side A?", "Deck is playing side A")

        client.send(Command.Pause)

        await rcv.expect(State.PausedA)

        check("Did the deck pause?", "Deck is paused on side A")

        client.send(Command.Pause)

        await rcv.expect(State.PlayingA)

        check("Did the deck start playing side A again?", "Deck is playing side A")

        client.send(Command.FastForward)

        await rcv.expect(State.FastForwarding)
        await rcv.expect(State.Stopped)

        client.send(Command.PlayB)

        await rcv.expect(State.PlayingB)

        check(
            "Did the deck fast-forward and start playing side B?",
            "Deck is playing side B",
        )

        client.send(Command.Pause)

        await rcv.expect(State.PausedB)

        check("Did the deck pause?", "Deck is paused on side A")

        client.send(Command.Pause)

        await rcv.expect(State.PlayingB)

        check("Did the deck start playing side B again?", "Deck is playing side B")

        client.send(Command.Eject)

        await rcv.expect(State.Ejected)

        check("Did the deck eject the tape?", "Deck has ejected")

    client.events.remove_listener("state", log_state)

    client.close()


if __name__ == "__main__":
    run_tests(__name__)
