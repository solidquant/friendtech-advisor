import zmq
import json
import asyncio
import datetime
import requests
import aioprocessing

from web3 import Web3
from typing import Any, Dict
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
    get_cached_users_dict,
    get_cached_supplies_dict,
    get_cached_holders_dict,
    update_users_dict,
    update_supplies_dict,
    update_holders_dict,
    get_price_history_of_subject,
    extract_n_users_history,
    get_top_supplies,
)
from constants import (
    BASE_WSS_URL,
    BASE_ALCHEMY_URL,
    FT_ADDRESS,
)


def get_subject_info_lite(subject: str) -> Dict[str, Any]:
    url = f'https://prod-api.kosetto.com/users/{subject}'
    res = requests.get(url)
    info = res.json()
    return {
        'twitter_username': info['twitterUsername'],
        'twitter_name': info['twitterName'],
        'twitter_uid': info['twitterUserId'],
        'twitter_img': info['twitterPfpUrl'],
    }


async def event_handler(event_queue: aioprocessing.AioQueue):
    port = 7777
    
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f'tcp://*:{port}')
    
    w3 = Web3(Web3.HTTPProvider(BASE_ALCHEMY_URL))
    
    top_info = {}
    
    cached_trades_array = get_cached_trades_array()
    users = get_cached_users_dict(cached_trades_array)
    supplies = get_cached_supplies_dict(cached_trades_array)
    top_supplies = get_top_supplies(supplies, 10)
    
    for subject, _ in top_supplies.items():
        if subject not in top_info:
            top_info[subject] = get_subject_info_lite(subject)
            print(f'{subject} data retrieved')
    
    last_trades = deque(maxlen=20)
    last_trades_tx_hash = deque(maxlen=20)
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
                users = update_users_dict(users, new_trades)
                supplies = update_supplies_dict(supplies, new_trades)
                
                now = datetime.datetime.now()
                
                # Publish newly created TXs
                newly_added = 0
                for trade in new_trades:
                    if trade.tx_hash not in last_trades_tx_hash:
                        multiplier = 1 if trade.is_buy else -1
                        amount = trade.share_amount * multiplier
                        new_trade = {
                            'ts': int(now.timestamp() * 1000),
                            'block': trade.block,
                            'tx_hash': trade.tx_hash,
                            'trader': trade.trader,
                            'subject': trade.subject,
                            'amount': amount,
                            'supply': trade.supply,
                        }
                        last_trades.append(new_trade)
                        last_trades_tx_hash.append(trade.tx_hash)
                        socket.send_string(json.dumps({
                            'type': 'new_tx',
                            'tx': new_trade,
                        }))
                        newly_added += 1
                        
                # Get users history
                users_history = extract_n_users_history(users['users_history'])
                        
                # Get top 100 subjects
                top_supplies = get_top_supplies(supplies, 10)
                
                top_supplies_formatted = []
                for subject, supply in top_supplies.items():
                    if subject not in top_info:
                        top_info[subject] = get_subject_info_lite(subject)
                        print(f'{subject} data retrieved')
                    top_supplies_formatted.append({
                        'subject': subject,
                        'supply': supply,
                        **top_info[subject]
                    })
                        
                msg = {
                    'type': 'new_block',
                    'block': block_number,
                    'txs': list(reversed(last_trades)),
                    'users_history': users_history,
                    'top_supplies': top_supplies_formatted,
                }
                socket.send_string(json.dumps(msg))
                last_updated_block = block_number
                
                print(f'[{now}] Block #{block_number}: {newly_added} txs')
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
    