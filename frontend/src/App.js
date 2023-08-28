import { Navbar, Stats, Trending } from "./components";
import io from 'socket.io-client';

const socket = io.connect('http://localhost:5555', {reconnect: true});

function App() {
  return (
    <div className="App">
      <Navbar />
      <Stats />
      <Trending socket={socket} />
    </div>
  );
}

export default App;
