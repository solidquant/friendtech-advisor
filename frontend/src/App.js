import { Navbar, Stats, Top, Transactions } from "./components";
import io from 'socket.io-client';

const socket = io.connect(process.env.HOST, {reconnect: true});

function App() {
  return (
    <div className="App">
      <Navbar />
      <Stats socket={socket} />
      <Top socket={socket} />
      <Transactions socket={socket} />
    </div>
  );
}

export default App;
