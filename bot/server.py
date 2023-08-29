import zmq
import json
import asyncio
import aioprocessing

from web3 import Web3
from functools import partial
from collections import deque

from streams import stream_new_blocks
from utils import reconnecting_websocket_loop
from subjects import (
    load_from_range,
)
from web_data import (
    BLOCK,
    get_cached_trades_array,
    get_cached_supplies_dict,
    get_cached_holders_dict,
    update_supplies_dict,
    update_holders_dict,
    get_price_history_of_subject,
    get_top_supplies,
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
    
    cached_trades_array = get_cached_trades_array()
    supplies = get_cached_supplies_dict(cached_trades_array)
    
    last_hundred_blocks = deque(maxlen=100)
    last_updated_block = cached_trades_array[-1, BLOCK]
    
    while True:
        try:
            data = await event_queue.coro_get()
            
            if data['type'] == 'block':
                block_number = data['block_number']
                # base_fee = data['base_fee']
                
                from_block = block_number if last_updated_block == 0 else last_updated_block
                new_trades = load_from_range(w3,
                                            FT_ADDRESS,
                                            from_block,
                                            block_number,
                                            2000)
                last_hundred_blocks.append(new_trades)
                supplies = update_supplies_dict(supplies, new_trades)
                
                # Publish newly created TXs
                trades_list = []
                for trade in new_trades:
                    if trade.block == block_number:
                        multiplier = 1 if trade.is_buy else -1
                        amount = trade.share_amount * multiplier
                        trades_list.append({
                            'trader': trade.trader,
                            'subject': trade.subject,
                            'amount': amount,
                            'supply': trade.supply,
                        })
                        
                # Get top 100 subjects
                top_supplies = get_top_supplies(supplies, 100)
                        
                msg = {
                    'type': 'new_block',
                    'block': block_number,
                    'txs': trades_list,
                    'top_supplies': top_supplies,
                }
                socket.send_string(json.dumps(msg))
                last_updated_block = block_number
                print(msg)
        except Exception as e:
            print(e)


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
    