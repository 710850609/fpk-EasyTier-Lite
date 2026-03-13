import { fetchNigger } from './fetchNigger.js';
import { fetchSbgov } from './fetchSbgov.js';

async function updatePeers() {
  const peersList = await Promise.all([
    fetchNigger(), 
    fetchSbgov()
  ]);
  const peers = peersList.flat();
  
  console.log(peers)
}

updatePeers();