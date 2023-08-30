import { useEffect, useState } from 'react';
import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en';

TimeAgo.addDefaultLocale(en);
const timeAgo = new TimeAgo('en-US');

const Transactions = ({ socket }) => {
    const [txs, setTxs] = useState([]);

    useEffect(() => {
        socket.on('event', (evt) => {
            setTxs(evt.txs);
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
                filteredTxs.map(tx => (
                    <SingleTransaction tx={tx} />
                ))
            }
        </div>
    );
};

const getPrice = (supply, amount) => {
    let sum1 = (supply == 0) ? 0 : (supply - 1) * supply * (2 * (supply - 1) + 1) / 6;
    let sum2 = (supply == 0 && amount == 1) ? 0 : (supply - 1 + amount) * (supply + amount) * (2 * (supply - 1 + amount) + 1) / 6;
    let summation = sum2 - sum1;
    return summation * (10 ** 18) / 16000;
};

const SingleTransaction = ({ tx }) => {
    let event = '';
    let eventColor = {};

    if (tx.trader == tx.subject && tx.amount == 1 && tx.supply == 1) {
        event = 'User Registered 👋';
        eventColor = {background: '#2d3436', color: 'white'};
    } else if (tx.amount < 0) {
        event = `SELL: ${Math.abs(tx.amount)}`;
        eventColor = {color: '#F45532', fontWeight: 'bold'};
    } else if (tx.amount > 0) {
        event = `BUY: ${tx.amount}`;
        eventColor = {color: '#00b894', fontWeight: 'bold'};
    }

    let price = getPrice(tx.supply, 1) / (10 ** 18);

    return (
        <div className="tx">
            {
                (event == '') ? <></> : (
                    <div className="tx-event">
                        <span style={eventColor}>{event}</span>
                    </div>
                )
            }
            <div className="tx-subject">🔑 {tx.subject}</div>
            <div className="tx-supply">
                Supply: <span style={{fontWeight: 'bold'}}>{tx.supply}</span> / Price: <span style={{fontWeight: 'bold'}}>{price} ETH</span>
            </div>
            <p>Trader: {tx.trader}</p>
        </div>
    );
};

export default Transactions;