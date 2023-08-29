import os
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Dict, List
from operator import itemgetter

from constants import _DIR
from subjects import Trade

TRADER = 0
SUBJECT = 1
IS_BUY = 2
SHARE_AMOUNT = 3
ETH_AMOUNT = 4
PROTOCOL_ETH_AMOUNT = 5
SUBJECT_ETH_AMOUNT = 6
SUPPLY = 7
BLOCK = 8

"""
1. Most expensive keys: Subject's latest snapshot of supplies (top 100)
2. Price change of subject: trade history of subject (momentum trading)
3. Current holders
4. Most profitable trader: trade history of trader (copy trading)
"""
def get_cached_trades_array() -> np.ndarray:
    trades = pd.read_csv(_DIR / '.cached-trades.csv', low_memory=False)
    trades_array = trades.values
    return trades_array


def get_cached_supplies_dict(trades_array: np.ndarray or None) -> Dict[str, int]:
    if type(trades_array) == type(None):
        trades_array = get_cached_trades_array()
    cached_supplies = {}
    for i in range(trades_array.shape[0]):
        row = trades_array[i]
        cached_supplies[row[SUBJECT]] = row[SUPPLY]
    return cached_supplies


def get_cached_holders_dict(trades_array: np.ndarray or None) -> Dict[str, Dict[str, int]]:
    if type(trades_array) == type(None):
        trades_array = get_cached_trades_array()
    cached_holders = {}
    for i in range(trades_array.shape[0]):
        row = trades_array[i]
        trader = row[TRADER]
        subject = row[SUBJECT]
        if subject not in cached_holders:
            cached_holders[subject] = {}
        if trader not in cached_holders[subject]:
            cached_holders[subject][trader] = 0
        multiplier = 1 if row[IS_BUY] else -1
        amount = row[SHARE_AMOUNT] * multiplier
        cached_holders[subject][trader] += amount
    return cached_holders


def make_supplies_dict(trades: List[Trade]) -> Dict[str, int]:
    supplies = {}
    for trade in trades:
        supplies[trade.subject] = trade.supply
    return supplies


def update_supplies_dict(prev_supplies: Dict[str, int], trades: List[Trade]) -> Dict[str, int]:
    new_supplies = make_supplies_dict(trades)
    prev_supplies.update(new_supplies)
    return prev_supplies


def update_holders_dict(prev_holders: Dict[str, Dict[str, int]], trades: List[Trade]) -> Dict[str, Dict[str, int]]:
    for trade in trades:
        trader = trade.trader
        subject = trade.subject
        if subject not in prev_holders:
            prev_holders[subject] = {}
        if trader not in prev_holders[subject]:
            prev_holders[subject][trader] = 0
        multiplier = 1 if trade.is_buy else -1
        amount = trade.share_amount * multiplier
        prev_holders[subject][trader] += amount
    return prev_holders


def get_price_history_of_subject(trades_array: np.ndarray, subject: str) -> np.ndarray:
    return trades_array[trades_array[SUBJECT] == subject]


def get_top_supplies(supplies: Dict[str, int], n: int) -> Dict[str, int]:
    return dict(sorted(supplies.items(), key=itemgetter(1), reverse=True)[:n])


if __name__ == '__main__':
    trades_array = get_cached_trades_array()
    last_updated_block = trades_array[-1][BLOCK]
    print(last_updated_block)
    
    holders = get_cached_holders_dict(trades_array)
    supplies = get_cached_supplies_dict(trades_array)
    
    top_supplies = get_top_supplies(supplies, 10)
    print(top_supplies)