import json
import asyncio
import websockets
import aioprocessing

from web3 import Web3


async def stream_new_blocks(wss_url: str, event_queue: aioprocessing.AioQueue):    
    async with websockets.connect(wss_url) as ws:
        wss = Web3.WebsocketProvider(wss_url)
        subscription = wss.encode_rpc_request('eth_subscribe', ['newHeads'])
        
        await ws.send(subscription)
        _ = await ws.recv()

        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=60 * 10)
            block = json.loads(msg)['params']['result']
            block_number = int(block['number'], base=16)
            base_fee = int(block['baseFeePerGas'], base=16)
            event = {
                'type': 'block',
                'block_number': block_number,
                'base_fee': base_fee,
            }
            event_queue.put(event)
