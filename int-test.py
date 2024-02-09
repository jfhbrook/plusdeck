import asyncio

from plusdeck import Command, State, Side, PlusDeckProtocol, create_connection

PORT = '/dev/ttyUSB0'

class TestProtocol(PlusDeckProtocol):
    def on_state(self, state):
        print(state)


async def main():
    transport, protocol = await create_connection(PORT, TestProtocol)

    transport.write(b"\x0b\n")

    print("wrote to transport")

    await asyncio.sleep(10)


loop = asyncio.get_event_loop()

loop.run_until_complete(main())
