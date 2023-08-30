# Node.js backend server for friend.tech visualizer

The backend is built using Express.js.

This is a very simple backend server that connects to the Python "bot" data server (server.py) using ZeroMQ.

When a frontend client connects to the server, it will automatically subscribe to the Python ZeroMQ publisher server and stream data whenever a new block is created on the Base network.