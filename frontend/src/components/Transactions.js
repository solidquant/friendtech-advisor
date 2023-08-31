import { useEffect, useState } from 'react';
import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en';

import utils from './utils';

TimeAgo.addDefaultLocale(en);
const timeAgo = new TimeAgo('en-US');

const Transactions = ({ socket }) => {
    const [txs, setTxs] = useState([]);

    useEffect(() => {
        socket.on('event', (evt) => {
            setTxs(evt.txs);
        });

        socket.on('transaction', (tx) => {
            console.log(tx);
        });
    }, []);

    return (
        <div className="Transactions">
            <div className="title">✅ Recent Transactions</div>
            <div className="items">
                <TransactionsList txs={txs} />
            </div>
        </div>
    );
};

const TransactionsList = ({ txs }) => {
    const blocks = [...new Set(txs.map(tx => tx.block))];

    return blocks.map((block, idx) => (
        <BlockTransactions key={idx} block={block} txs={txs} />
    ));
};

const BlockTransactions = ({ block, txs }) => {
    const filteredTxs = txs.filter(tx => tx.block == block);
    const time = timeAgo.format(filteredTxs[0].ts, 'twitter');

    return (
        <div className="block-txs">
            <div className="block-num">
                ▪️ Block #{block.toLocaleString()} <span>{time} ago</span>
            </div>
            {
                filteredTxs.map((tx, idx) => (
                    <SingleTransaction key={idx} tx={tx} />
                ))
            }
        </div>
    );
};

const SingleTransaction = ({ tx }) => {
    let event = '';
    let eventColor = {};

    if (tx.trader == tx.subject && tx.amount == 1 && tx.supply == 1) {
        event = 'User Registered 👋';
        eventColor = {background: '#2d3436', color: 'white', paddingLeft: '0.5rem', paddingRight: '0.5rem' };
    } else if (tx.amount < 0) {
        event = `SELL: ${Math.abs(tx.amount)}`;
        eventColor = {color: '#F45532', fontWeight: 'bold'};
    } else if (tx.amount > 0) {
        event = `BUY: ${tx.amount}`;
        eventColor = {color: '#00b894', fontWeight: 'bold'};
    }

    let price = utils.getPrice(tx.supply, 1) / (10 ** 18);

    return (
        <div className="tx">
            {
                (event == '') ? <></> : (
                    <div className="tx-event">
                        <span style={eventColor}>{event}</span>
                    </div>
                )
            }
            <div className="tx-subject">
                <a  href={`https://basescan.org/tx/${tx.tx_hash}`} target="_blank">🔑 {tx.subject}</a>
            </div>
            <div className="tx-supply">
                Supply: <span style={{fontWeight: 'bold'}}>{tx.supply}</span> / Price: <span style={{fontWeight: 'bold'}}>{price} ETH</span>
            </div>
            <p>Trader: {tx.trader}</p>
        </div>
    );
};

export default Transactions;