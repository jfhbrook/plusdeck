import asyncio

from plusdeck import Command, State, create_connection

PORT = '/dev/ttyUSB0'

async def main():
    client = await create_connection(PORT)

    client.events.on('state', lambda st: print(st))

    await asyncio.sleep(10)

    client.send(Command.PlaySideA)

    await asyncio.sleep(10)


loop = asyncio.get_event_loop()

loop.run_until_complete(main())
