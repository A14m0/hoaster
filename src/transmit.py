import asyncio
from loguru import logger as l
import os
from websockets.asyncio.server import serve

def websocket_start(config):
    l.info("Starting WebSocket transport...")

    # keep track of some state
    STATE = {
        'index': 0,
        'repeat': 0
    }

    # set up our websocket server
    async def run_config(websocket):
        l.info("Received connection")
        # loop until we are done
        while STATE['index'] < len(config['payloads']):
            # delay for some amount of time
            l.debug("Sleeping...")
            await asyncio.sleep(config['payloads'][STATE['index']]['delay'])

            # read our payload
            l.debug("Reading payload...")
            payload = config['payloads'][STATE['index']]['payload']
            if not os.path.exists(payload):
                l.error(f"Payload path '{payload}' doesn't exist")
                exit(2)

            # read the data and transmit
            with open(payload) as f:
                await websocket.send(f.read())
            l.info("Transmitted payload")

            # update our state
            if STATE['repeat'] >= config['payloads'][STATE['index']]['repeat']:
                STATE['index'] += 1
                STATE['repeat'] = 0
            else:
                STATE['repeat'] += 1

            l.debug(f"Current state: {STATE}")

        # we're done, bail
        l.warning(f"Hit end of available payloads in config (count: {len(config['payloads'])}). Halting...")
        exit(0)

    # serve stuff up asynchronously
    async def main():
        async with serve(run_config, "localhost", config['port']) as server:
            # issue: this keeps serving if something else calls `exit`...
            await server.serve_forever()

    # run the thing
    asyncio.run(main())

def tcp_start(config):
    l.warning("Currently, TCP is under development. Come back soon!")
    exit(0)





# define the transports and their start function mapping
TRANSPORTS = {
    "websocket": websocket_start,
    "tcp": tcp_start
}

def transmit_main(config):
    l.info("Starting transmitter main...")

    # figure out what transport we are going to use
    if config["transport"] not in TRANSPORTS.keys():
        l.error(f"Unsupported transport '{config['transport']}. Supported transports are {TRANSPORTS.keys()}")
        exit(2)

    # run the transport
    TRANSPORTS[config['transport']](config)
