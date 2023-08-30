import os
import csv
import time
import pandas as pd
from twitter.scraper import Scraper

from web3 import Web3
from tqdm import tqdm
from typing import List, Dict, Any

from constants import (
    _DIR,
    BASE_ALCHEMY_URL,
    FT_ADDRESS,
    FT_ABI,
    TWITTER_EMAIL,
    TWITTER_USERNAME,
    TWITTER_PASSWORD,
)


class Trade:
    
    def __init__(self,
                 trader: str,
                 subject: str,
                 is_buy: bool,
                 share_amount: int,
                 eth_amount: int,
                 protocol_eth_amount: int,
                 subject_eth_amount: int,
                 supply: int,
                 block: int,
                 tx_hash: str):
        
        self.trader = trader
        self.subject = subject
        self.is_buy = is_buy
        self.share_amount = share_amount
        self.eth_amount = eth_amount
        self.protocol_eth_amount = protocol_eth_amount
        self.subject_eth_amount = subject_eth_amount
        self.supply = supply
        self.block = block
        self.tx_hash = tx_hash
        
    def cache_row(self):
        return [
            self.trader,
            self.subject,
            self.is_buy,
            self.share_amount,
            self.eth_amount,
            self.protocol_eth_amount,
            self.subject_eth_amount,
            self.supply,
            self.block,
            self.tx_hash,
        ]
        
        
def load_cached_trades() -> (int, List[Trade]):
    from_block = 0
    trades = []
    
    files = [f for f in os.listdir(_DIR) if '.csv' in f]
    
    if len(files) > 0:
        file = [f for f in files if f == '.cached-trades.csv'][0]
        f = open(_DIR / file, 'r')
        rdr = csv.reader(f)
        
        for row in rdr:
            if row[0] == 'trader':
                continue
            trade = Trade(trader=row[0],
                          subject=row[1],
                          is_buy=row[2],
                          share_amount=int(row[3]),
                          eth_amount=int(row[4]),
                          protocol_eth_amount=int(row[5]),
                          subject_eth_amount=int(row[6]),
                          supply=int(row[7]),
                          block=int(row[8]),
                          tx_hash=row[9])
            trades.append(trade)
            from_block = max(trade.block, from_block)  # last updated block
            
    return from_block, trades


def cache_synced_trades(trades: List[Trade], last_block: int = 0):
    file = _DIR / f'.cached-trades.csv'
    if not os.path.exists(file):
        f = open(file, 'w', newline='')
        wr = csv.writer(f)
        columns = ['trader', 'subject', 'is_buy', 'share_amount', 'eth_amount', 'protocol_eth_amount', 'subject_eth_amount', 'supply', 'block', 'tx_hash']
        wr.writerow(columns)
        for trade in trades:
            wr.writerow(trade.cache_row())
        f.close()
        print(f'Saved trade data to cache ({len(trades)} trades)')
    else:
        if last_block == 0:
            cached = pd.read_csv(file)
            last_block = cached.iloc[-1]['block']
        f = open(file, 'a', newline='')
        wr = csv.writer(f)
        _trades = [t for t in trades if t.block > last_block]
        for trade in _trades:
            wr.writerow(trade.cache_row())
        f.close()
        print(f'Appended {len(_trades)} new trade data to cache ({len(trades)} trades)')
    
    
def load_from_range(w3: Web3,
                    ft_address: str,
                    from_block: int,
                    to_block: int,
                    chunk: int) -> List[Trade]:
    trades = []
    ft = w3.eth.contract(address=ft_address, abi=FT_ABI)

    if to_block - from_block > chunk:
        block_range = list(range(from_block, to_block, chunk))
        if block_range[-1] < to_block:
            block_range.append(to_block)
        request_params = [(block_range[i], block_range[i + 1]) for i in range(len(block_range) - 1)]
        _range = tqdm(request_params,
                      total=len(request_params),
                      ncols=100,
                      desc=f'Friendtech Trade {ft_address[:10]}... Sync',
                      ascii=' =',
                      leave=True)
    else:
        request_params = [(from_block, to_block)]
        _range = request_params
    
    for params in _range:
        events = ft.events.Trade.get_logs(fromBlock=params[0], toBlock=params[1])
        for event in events:
            block = event.blockNumber
            tx_hash = event.transactionHash.hex()
            args = event.args
            trade = Trade(args.trader,
                          args.subject,
                          args.isBuy,
                          args.shareAmount,
                          args.ethAmount,
                          args.protocolEthAmount,
                          args.subjectEthAmount,
                          args.supply,
                          block,
                          tx_hash)
            trades.append(trade)
    
    return trades


def load_all_subjects_from_friendtech(https_url: str,
                                      ft_address: str,
                                      from_block: int,
                                      chunk: int) -> (int, List[str]):
    _from_block, trades = load_cached_trades()
    from_block = max(_from_block + 1, from_block)
    
    w3 = Web3(Web3.HTTPProvider(https_url))
    to_block = w3.eth.get_block_number()
    
    if len(trades) != 0 and from_block == to_block:
        return trades
    
    new_trades = load_from_range(w3, ft_address, from_block, to_block, chunk)
    trades.extend(new_trades)
            
    return to_block, trades


def update_balance_and_shares(states: dict, trades: List[Trade]) -> Dict[str, Any]:
    for trade in trades:
        trader = trade.trader
        subject = trade.subject
        is_buy = trade.is_buy
        amount = trade.share_amount
        supply = trade.supply
        
        if trader not in states['balance']:
            states['balance'][trader] = {}
            
        if subject not in states['balance'][trader]:
            states['balance'][trader][subject] = 0
            
        if is_buy:
            states['balance'][trader][subject] += amount
        else:
            states['balance'][trader][subject] -= amount

        states['shares'][subject] = supply
    return states


def make_states_dict(to_block: int, trades: List[Trade]) -> Dict[str, Any]:
    states = {
        'block': to_block,
        'balance': {},
        'shares': {},
    }
    states = update_balance_and_shares(states, trades)
    return states


def get_twitter_user(scraper: Scraper, twitter_id: str) -> Dict[str, Any]:
    user = scraper.users_by_id([twitter_id])
    legacy = user[0]['data']['user']['result']['legacy']
    return {
        'followers': legacy.get('followers_count', 0),
        'following': legacy.get('friends_count', 0),
        'tweets': legacy.get('statuses_count', 0),
        'verified': legacy.get('verified', False),
    }
    

def get_subject_info(scraper: Scraper, subject: str) -> Dict[str, Any]:
    url = f'https://prod-api.kosetto.com/users/{subject}'
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        twitter_user = get_twitter_user(scraper, json_data['twitterUserId'])
        info = {**json_data, **twitter_user}
        formatted_info = {
            'id': info['id'],
            'address': info['address'],
            'twitter_username': info['twitterUsername'],
            'twitter_name': info['twitterName'],
            'twitter_uid': info['twitterUserId'],
            'twitter_img': info['twitterPfpUrl'],
            'followers': info['followers'],
            'following': info['following'],
            'tweets': info['tweets'],
            'verified': info['verified'],
        }
        return formatted_info


def load_subject_info(subjects: List[str]):
    scraper = Scraper(TWITTER_EMAIL,
                      TWITTER_USERNAME,
                      TWITTER_PASSWORD,
                      save=False,
                      pbar=False)
    files = [f for f in os.listdir(_DIR) if '.csv' in f]
    
    subject_info = {}
    
    if len(files) > 0:
        file = [f for f in files if f == '.cached-subjects.csv']
        if file:
            file = file[0]
            cached_info = pd.read_csv(_DIR / file)
            cached_info = cached_info.T.to_dict()
            for _, _info in cached_info.items():
                subject_info[_info['address']] = _info
        
    for subject in tqdm(subjects):
        if subject not in subject_info:
            info = get_subject_info(scraper, subject)
            if info:
                subject_info[subject] = _info
            time.sleep(1)
    
    f = open(_DIR / f'.cached-subjects.csv', 'w', newline='')
    wr = csv.writer(f)
    columns = ['id', 'address', 'twitter_username', 'twitter_name', 'twitter_uid', 'twitter_img', 'followers', 'following', 'tweets', 'verified']
    wr.writerow(columns)
    for _, info in subject_info.items():
        wr.writerow(list(info.values()))
    f.close()
    print(f'Saved subject info data to cache ({len(subject_info)} trades)')


if __name__ == '__main__':
    import requests
    import pandas as pd
    
    w3 = Web3(Web3.HTTPProvider(BASE_ALCHEMY_URL))
    
    # while True:
    #     block = w3.eth.get_block('latest')
    #     block_number = block.number
    #     print(block_number)
        
    #     trades = load_from_range(w3, FT_ADDRESS, block_number, block_number, 2000)

    #     for trade in trades:
    #         print(trade.cache_row())
            
    #     time.sleep(1)
    
    to_block, trades = load_all_subjects_from_friendtech(BASE_ALCHEMY_URL, FT_ADDRESS, 2430440, 2000)
    cache_synced_trades(trades)
    
    # trades_list = [t.cache_row() for t in trades]
    # trades_df = pd.DataFrame(trades_list)
    # trades_df.columns = ['trader', 'subject', 'is_buy', 'share_amount', 'eth_amount', 'protocol_eth_amount', 'subject_eth_amount', 'supply', 'block']
    
    # subjects = list(trades_df['subject'].unique())
    # subject_info = load_subject_info(subjects[:100])