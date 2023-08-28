import eth_abi
import asyncio
import websockets
from web3 import Web3

from typing import Callable

from subjects import Trade
from constants import FT_ABI, FT_ADDRESS


async def reconnecting_websocket_loop(stream_fn: Callable, tag: str):
    while True:
        try:
            await stream_fn()

        except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK) as e:
            print(f'{tag} websocket connection closed: {e}')
            print('Reconnecting...')
            await asyncio.sleep(2)

        except Exception as e:
            print(f'An error has occurred with {tag} websocket: {e}')
            await asyncio.sleep(2)
            
            
def get_price(supply: int, amount: int) -> int:
    sum1 = 0 if supply == 0 else (supply - 1) * supply * (2 * (supply - 1) + 1) / 6
    sum2 = 0 if supply == 0 and amount == 1 else (supply - 1 + amount) * (supply + amount) * (2 * (supply - 1 + amount) + 1) / 6
    summation = sum2 - sum1
    return summation * (10 ** 18) / 16000


def get_buy_price_after_fee(supply: int,
                            amount: int,
                            protocol_fee: int,
                            subject_fee: int) -> int:
    price = get_price(supply, amount)
    protocol_fee = price * protocol_fee / (10 ** 18)
    subject_fee = price * subject_fee / (10 ** 18)
    return price + protocol_fee + subject_fee


def get_sell_price_after_fee(supply: int,
                             amount: int,
                             protocol_fee: int,
                             subject_fee: int) -> int:
    price = get_price(supply, amount)
    protocol_fee = price * protocol_fee / (10 ** 18)
    subject_fee = price * subject_fee / (10 ** 18)
    return price - protocol_fee - subject_fee


def get_all_trades(w3: Web3, from_block: int, to_block: int):
    ft = w3.eth.contract(address=FT_ADDRESS, abi=FT_ABI)
    events = ft.events.Trade.get_logs(fromBlock=from_block, toBlock=to_block)
    trades = []
    for event in events:
        block = event.blockNumber
        args = event.args
        trade = Trade(args.trader,
                        args.subject,
                        args.isBuy,
                        args.shareAmount,
                        args.ethAmount,
                        args.protocolEthAmount,
                        args.subjectEthAmount,
                        args.supply,
                        block)
        trades.append(trade)
    return trades