import { useEffect, useState } from 'react';

import utils from './utils';

const Top = ({ socket }) => {
    const [rankers, setRankers] = useState([]);

    useEffect(() => {
        socket.on('event', (evt) => {
            setRankers(evt.top_supplies);
        })
    }, []);

    return (
        <div className="Top">
            <div className="title">💎 Top 10 Supplies</div>
            <div className="items">
                {
                    rankers.map((ranker, idx) => (
                        <Ranker key={idx} info={ranker} />
                    ))
                }
            </div>
        </div>
    );
};

const Ranker = ({ info }) => {
    let price = utils.getPrice(info.supply, 1) / (10 ** 18);

    return (
        <div className="top-ranker">
            <div className="ranker-twitter">
                <a href={`https://twitter.com/${info.twitter_username}`} target="_blank">
                    <img src={info.twitter_img} /> @{info.twitter_username}
                </a>
            </div>
            <div className="ranker-subject">🏆 {info.subject}</div>
            <div className="ranker-info">
                <div className="ranker-supply">
                    Supply: <span style={{fontWeight: 'bold'}}>{info.supply}</span> / Price: <span style={{fontWeight: 'bold'}}>{price} ETH</span>
                </div>
            </div>
        </div>
    );
};

export default Top;