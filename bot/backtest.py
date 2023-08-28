import os
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm

from constants import _DIR

TRADER = 0
SUBJECT = 1
IS_BUY = 2
SHARE_AMOUNT = 3
ETH_AMOUNT = 4
PROTOCOL_ETH_AMOUNT = 5
SUBJECT_ETH_AMOUNT = 6
SUPPLY = 7
BLOCK = 8

if os.path.exists(_DIR / '.shares.npy'):
    with open(_DIR / '.shares.npy', 'rb') as f:
        shares_array = np.load(f)
        
    with open(_DIR / '.db.pkl', 'rb') as fr:
        shares_array_pkl = pickle.load(fr)
        
    max_block = shares_array_pkl['block']
    subjects_id = shares_array_pkl['subjects_id']
    print(shares_array)
else:
    # Initial setup
    trades = pd.read_csv(_DIR / '.cached-trades.csv', low_memory=False)

    # traders = list(trades['trader'].unique())
    subjects = list(trades['subject'].unique())
    subjects_id = {subject: id for id, subject in enumerate(subjects)}

    min_block = trades.iloc[0]['block']
    max_block = trades.iloc[-1]['block']

    trades_array = trades.values

    trades_array = trades_array[:, [TRADER, SUBJECT, IS_BUY, SHARE_AMOUNT, SUPPLY, BLOCK]]
    shares_array = np.zeros((max_block - min_block + 1, len(subjects)))

    for subject_id, subject in tqdm(enumerate(subjects), total=len(subjects)):
        filtered = trades_array[trades_array[:, 1] == subject]
        for i in range(filtered.shape[0]):
            row = filtered[i]
            block_idx = row[5] - min_block
            shares_array[block_idx, subject_id] = row[4]
            
    with open(_DIR / '.shares.npy', 'wb') as f:
        np.save(f, shares_array)
    
    with open(_DIR / '.db.pkl', 'wb') as fw:
        pickle.dump({
            'block': max_block,
            'subjects_id': subjects_id,    
        }, fw)
