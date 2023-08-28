import { useEffect, useState } from 'react';

const Trending = ({ socket }) => {
    useEffect(() => {
        socket.on('event', (evt) => {
            console.log(evt);
        })
    }, [socket]);

    return (
        <div className="Trending">
            <div className="title">🔥 Trending</div>
            <div className="items">
                <SubjectItem name={"item 1"} />
                <SubjectItem name={"item 2"} />
                <SubjectItem name={"item 3"} />
            </div>
        </div>
    );
}

const SubjectItem = ({ name }) => {
    return (
        <div className="SubjectItem">
            { name }
        </div>
    );
}

export default Trending;