// Fill blocks of various sizes via submit_data (DataAvailability pallet).
// Usage: node fill.mjs <sizeBytesPerTx> <numTxs> <label>
import { initialize, getKeyringFromSeed } from 'avail-js-sdk';
import { Keyring } from '@polkadot/api';

const RPC = 'ws://127.0.0.1:9944';
const sizePerTx = parseInt(process.argv[2] || '1048576', 10);
const numTxs = parseInt(process.argv[3] || '4', 10);
const label = process.argv[4] || 'block';

function makeData(n) {
  // random-ish bytes to avoid trivial compression effects in grid
  const buf = Buffer.alloc(n);
  for (let i = 0; i < n; i++) buf[i] = (i * 31 + 7) & 0xff;
  return '0x' + buf.toString('hex');
}

async function main() {
  const api = await initialize(RPC);
  const keyring = new Keyring({ type: 'sr25519' });
  const alice = keyring.addFromUri('//Alice');

  const startHeader = await api.rpc.chain.getHeader();
  const startNum = startHeader.number.toNumber();
  console.error(`start block #${startNum}, submitting ${numTxs} txs of ${sizePerTx} bytes each (label=${label})`);

  let nonce = (await api.rpc.system.accountNextIndex(alice.address)).toNumber();
  const data = makeData(sizePerTx);
  const blockHashes = new Set();
  const promises = [];
  for (let i = 0; i < numTxs; i++) {
    const tx = api.tx.dataAvailability.submitData(data);
    const p = new Promise((resolve) => {
      tx.signAndSend(alice, { nonce: nonce + i, app_id: 1 }, ({ status, dispatchError }) => {
        if (status.isInBlock) {
          blockHashes.add(status.asInBlock.toString());
          resolve();
        }
      }).catch((e) => { console.error('send err', e.message); resolve(); });
    });
    promises.push(p);
  }
  await Promise.all(promises);
  // give a moment for finalization context
  await new Promise(r => setTimeout(r, 2000));

  // For each block hash where our txs landed, fetch dims
  const results = [];
  for (const h of blockHashes) {
    const len = await api.rpc('kate_blockLength', h).catch(() => null);
    const header = await api.rpc.chain.getHeader(h);
    results.push({ hash: h, number: header.number.toNumber(), blockLength: len ? len.toJSON() : null });
  }
  console.log(JSON.stringify({ label, sizePerTx, numTxs, startNum, blocks: results }, null, 2));
  await api.disconnect();
  process.exit(0);
}
main().catch(e => { console.error(e); process.exit(1); });
