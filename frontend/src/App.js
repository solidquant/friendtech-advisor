import { Navbar, Stats, Transactions } from "./components";
import io from 'socket.io-client';

const socket = io.connect('http://localhost:5555', {reconnect: true});

function App() {
  return (
    <div className="App">
      <Navbar />
      <Stats socket={socket} />
      <Transactions socket={socket} />
    </div>
  );
}

export default App;
