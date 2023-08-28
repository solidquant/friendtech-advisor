const cors = require('cors');
const zmq = require('zeromq');

const app = require('express')();
app.use(cors());

const server = require('http').createServer(app);
const io = require('socket.io')(server, {
    cors: {
        origin: '*',
    },
});

const CONNECTIONS = {};

io.on('connection', (socket) => {
    const id = socket.conn.id;
    const sock = zmq.socket('sub');
    const port = 7777;
    sock.connect(`tcp://127.0.0.1:${port}`);
    sock.subscribe('');
    sock.on('message', function(message) {
        socket.emit('event', JSON.parse(message));
    });
    CONNECTIONS[id] = sock;
    console.log(`[OPEN: ${id}] Connections: ${Object.keys(CONNECTIONS).length}`);

    socket.on('disconnect', () => {
        const id = socket.conn.id;
        CONNECTIONS[id].close();
        delete CONNECTIONS[id];
        console.log(`[CLOSED: ${id}] Connections: ${Object.keys(CONNECTIONS).length}`);
    })
});

server.listen(5555, () => {
    console.log('Listening on 5555');
});