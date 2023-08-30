import { useEffect, useState } from 'react';

const Transactions = ({ socket }) => {
    const [txs, setTxs] = useState([]);

    useEffect(() => {
        socket.on('event', (evt) => {
            console.log(evt.txs);
            setTxs(evt.txs);
        });
    }, []);

    return (
        <div className="Trending">
            <div className="title">✅ Recent Transactions</div>
            <div className="items">
                {
                    txs.map((tx, idx) => (
                        <SubjectItem data={tx} key={idx} />
                    ))
                }
            </div>
        </div>
    );
}

const SubjectItem = ({ data }) => {
    return (
        <div className="SubjectItem">
            <p>Block: {data.block}</p>
            <p>Trader: {data.trader}</p>
            <p>Subject: {data.subject}</p>
            <p>Amount: {data.amount} / Supply: {data.supply}</p>
        </div>
    );
}

export default Transactions;