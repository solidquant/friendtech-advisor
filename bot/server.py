import zmq
import asyncio
import aioprocessing

from web3 import Web3
from functools import partial

from streams import stream_new_blocks
from utils import reconnecting_websocket_loop
from subjects import (
    load_from_range,
)
from constants import (
    BASE_WSS_URL,
    BASE_ALCHEMY_URL,
    FT_ADDRESS,
)


async def event_handler(event_queue: aioprocessing.AioQueue):
    port = 7777
    
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f'tcp://*:{port}')
    
    w3 = Web3(Web3.HTTPProvider(BASE_ALCHEMY_URL))
    
    while True:
        data = await event_queue.coro_get()
        
        if data['type'] == 'block':
            block_number = data['block_number']
            base_fee = data['base_fee']
            
            new_trades = load_from_range(w3,
                                         FT_ADDRESS,
                                         block_number,
                                         block_number,
                                         2000)
            print(data)
            print(new_trades)


if __name__ == '__main__':
    event_queue = aioprocessing.AioQueue()
    
    stream_thread = reconnecting_websocket_loop(
        partial(stream_new_blocks, BASE_WSS_URL, event_queue),
        tag='stream_thread'
    )
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([
        stream_thread,
        event_handler(event_queue),
    ]))    
    