// queryProof measurement harness (low overhead, native http keep-alive).
// Modes:
//   single  <hash> <ncells> <durationSec>   -> tight loop 1 worker, report count + latency percentiles
//   conc    <hash> <ncells> <N> <durationSec> -> N concurrent workers, report throughput + per-req avg wall
//   latency <method> <durationSec>           -> measure cheap RPC latency (system_health/chain_getHeader) in a loop
import http from 'node:http';

const RPC_HOST = '127.0.0.1';
const RPC_PORT = 9944;
const agent = new http.Agent({ keepAlive: true, maxSockets: 256 });

function rpc(method, params) {
  const body = JSON.stringify({ jsonrpc: '2.0', id: 1, method, params });
  return new Promise((resolve, reject) => {
    const req = http.request({ host: RPC_HOST, port: RPC_PORT, method: 'POST', path: '/',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }, agent },
      (res) => { let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d)); });
    req.on('error', reject);
    req.write(body); req.end();
  });
}

function cells(n) { const a = []; for (let i = 0; i < n; i++) a.push({ row: i % 32, col: (i * 7) % 64 }); return a; }
function pct(arr, p) { const s = [...arr].sort((a,b)=>a-b); return s[Math.min(s.length-1, Math.floor(p/100*s.length))]; }
function stats(lat) { return { n: lat.length, min: +pct(lat,0).toFixed(2), p50: +pct(lat,50).toFixed(2), p90: +pct(lat,90).toFixed(2), p99: +pct(lat,99).toFixed(2), max: +pct(lat,100).toFixed(2), mean: +(lat.reduce((a,b)=>a+b,0)/lat.length).toFixed(2) }; }

async function single(hash, ncells, dur) {
  const c = cells(ncells); const lat = []; const end = Date.now() + dur*1000;
  // randomize cell each iter to defeat any cache
  let k = 0;
  while (Date.now() < end) {
    const cc = c.map((x,i)=>({ row: (x.row + k) % 256, col: (x.col + k*3) % 512 }));
    const t = process.hrtime.bigint();
    await rpc('kate_queryProof', [cc, hash]);
    lat.push(Number(process.hrtime.bigint() - t) / 1e6);
    k++;
  }
  console.log(JSON.stringify({ mode:'single', ncells, durSec:dur, latencyMs: stats(lat), reqs: lat.length, rps: +(lat.length/dur).toFixed(2) }));
}

async function conc(hash, ncells, N, dur) {
  const c = cells(ncells); const end = Date.now() + dur*1000;
  let total = 0; const lat = [];
  async function worker(id) {
    let k = id*1000;
    while (Date.now() < end) {
      const cc = c.map((x)=>({ row: (x.row + k) % 256, col: (x.col + k*3) % 512 }));
      const t = process.hrtime.bigint();
      await rpc('kate_queryProof', [cc, hash]);
      lat.push(Number(process.hrtime.bigint() - t) / 1e6);
      total++; k++;
    }
  }
  const ws = []; for (let i=0;i<N;i++) ws.push(worker(i));
  await Promise.all(ws);
  console.log(JSON.stringify({ mode:'conc', N, ncells, durSec:dur, reqs: total, rps: +(total/dur).toFixed(2), perReqAvgWallMs: +(lat.reduce((a,b)=>a+b,0)/lat.length).toFixed(2), latencyMs: stats(lat) }));
}

async function latency(method, dur) {
  const params = method === 'chain_getHeader' ? [] : [];
  const lat = []; const end = Date.now() + dur*1000;
  while (Date.now() < end) {
    const t = process.hrtime.bigint();
    await rpc(method, params);
    lat.push(Number(process.hrtime.bigint() - t)/1e6);
    await new Promise(r=>setTimeout(r, 50)); // sample, not flood
  }
  console.log(JSON.stringify({ mode:'latency', method, durSec:dur, latencyMs: stats(lat), samples: lat.length }));
}

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'single') await single(rest[0], parseInt(rest[1]), parseInt(rest[2]));
else if (mode === 'conc') await conc(rest[0], parseInt(rest[1]), parseInt(rest[2]), parseInt(rest[3]));
else if (mode === 'latency') await latency(rest[0], parseInt(rest[1]));
else { console.error('bad mode'); process.exit(1); }
process.exit(0);
