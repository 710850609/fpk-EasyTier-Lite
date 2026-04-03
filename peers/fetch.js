import { fetchNigger } from './fetchNigger.js';
import { fetchSbgov } from './fetchSbgov.js';
import fs from 'fs';

async function updatePeers() {
  const peersList = await Promise.all([
    fetchAstral(),
    fetchNigger(), 
    fetchSbgov()
  ]);
  const peers = peersList.flat();
  
  try {
    fs.writeFileSync('peer-list.txt', peers.join('\n'));
    console.log('文件已成功写入！');
  } catch (err) {
    console.error('写入失败:', err);
  }
  
  console.log(peers);
}

updatePeers();
