#!/usr/bin/env python3
"""Generate GitBook markdown pages for Celestia and Ethereum/PeerDAS threat models."""

import json
import os
import re
import sys

# ── Paths ──────────────────────────────────────────────────────
CELESTIA_JSON = "/Users/jyoo/work/bonda/bonda-frontend/lib/data/celestia-threats.json"
ETHEREUM_JSON = "/Users/jyoo/work/bonda/bonda-frontend/lib/data/ethereum-threats.json"
CELESTIA_OUT = "/Users/jyoo/bonda-docs/celestia/threats"
ETHEREUM_OUT = "/Users/jyoo/bonda-docs/ethereum/threats"

# ── STRIDE category from SID ──────────────────────────────────
STRIDE_MAP = {
    "S": "Spoofing",
    "T": "Tampering",
    "R": "Repudiation",
    "I": "Information Disclosure",
    "D": "Denial of Service",
    "E": "Elevation of Privilege",
    "P": "Protocol Design",
}


def stride_from_sid(sid: str) -> tuple:
    """Return (letter, full_name) from SID like CEL-D01, ETH-S01, G-CON-01, G-OPS-01."""
    sid_upper = sid.upper()
    m = re.match(r"CEL-([STRIDEP])\d+", sid_upper)
    if m:
        letter = m.group(1)
        return letter, STRIDE_MAP.get(letter, letter)
    m = re.match(r"ETH-([STRIDEP])\d+", sid_upper)
    if m:
        letter = m.group(1)
        return letter, STRIDE_MAP.get(letter, letter)
    if sid_upper.startswith("G-CON"):
        return "D", "Denial of Service"
    if sid_upper.startswith("G-OPS"):
        return "T", "Tampering"
    return "?", "Unknown"


def sid_to_filename(sid: str) -> str:
    return sid.lower() + ".md"


# ── English titles ─────────────────────────────────────────────

TITLES = {
    "CEL-D01": "Zero-cost Prevote-nil Censorship by 1/3 Cartel",
    "CEL-D02": "Large PFB Blockspace Monopoly — Low-cost Sustained Congestion Attack",
    "CEL-D04": "Evidence Subsystem Three Code Defects (Hash Truncation / Buffer Unbounded / Expiry Gap)",
    "CEL-D05": "ShrEx Client-side Unbounded Response Size — Defensive Coding Gap",
    "CEL-T01": "DAS-only Safety Model — Stale Documentation Misrepresents Security Guarantees",
    "CEL-E01": "SP1Blobstream 4-of-6 Multisig — Instant Upgrade Without Timelock",
    "CEL-S01": "DAS Selective Disclosure — Deceiving Light Nodes via Sybil Peers",
    "G-CON-01": "KYC Validator Concentration Enables Legal Censorship",
    "G-OPS-01": "Multi-surface Information Asymmetry — Structural Pattern (docs/spec/blog vs. code)",
    "CEL-D10": "NamespaceData Request — Worst-case Memory Reservation for Empty Namespace",
    "CEL-D12": "GetProposal Nil Pointer Panic — Node Crash via Block Sync Timing",
    "CEL-D13": "CheckTx Pre-gas Commitment Computation — Unlimited Blob Count",
    "CEL-D14": "ProcessProposal TxCache Bypass — Malicious Proposer Forces Full Commitment Recomputation",
    "CEL-D15": "blob.Subscribe Infinite Retry — CPU 100% Burn Without Backoff",
    "CEL-D17": "TxCache Key Mismatch — Blob Tx Cache Entry Permanent Leak Causing Validator OOM",
    "CEL-D03": "blacklistedHashes Unbounded Growth — Light Node OOM via Fake DataHash Injection",
    "CEL-D06": "EnableBlackListing Disabled by Default — Sybil Peer Reconnection Allowed",
    "CEL-P01": "Double Sign Flat 2% Slashing — Absence of Correlation Penalty (Protocol Design Gap)",
    "CEL-D11": "pendingSeenTracker Unbounded Memory Growth — Node OOM via Known On-chain Accounts + Future Sequence SeenTx",
    "ETH-S01": "Testing API JWT Authentication Missing",
    "ETH-S02": "Custody Group Node ID Grinding",
    "ETH-T01": "Blob Fee Denominator Fork-dependent Formula",
    "ETH-T02": "KZG Trusted Setup File Replacement",
    "ETH-T03": "Gloas Data Column Inclusion Proof Omission",
    "ETH-T04": "Cell Index Bounds Check Asymmetry",
    "ETH-T05": "Gloas Column Proof Verification",
    "ETH-R01": "Blob/DataColumn Equivocation Detection Failure",
    "ETH-D01": "Per-Account Blobpool Exhaustion (1-Wei Fee)",
    "ETH-D02": "Reconstruction Failure Discards All Verified Columns (Lighthouse)",
    "ETH-E01": "Reconstruction Failure Mode Inconsistency (Lighthouse vs. Prysm)",
}

# ── English translations ───────────────────────────────────────

TR = {
    "CEL-D01": {
        "details": (
            "A cartel controlling 1/3 of voting power can permanently censor targeted block proposals by "
            "sending nil votes at the prevote stage indefinitely. When the 2/3 threshold is not met, "
            "nil precommit followed by round timeout and proposer rotation repeats, leaving the targeted "
            "block permanently unfinalized. The slashing penalty is 0 TIA, and cartel members can avoid "
            "jail by signing just 10/10,000 blocks (min_signed_per_window=0.001, downtime_jail_duration=60s). "
            "The absence of a nil-vote evidence type makes it impossible to distinguish honest from "
            "malicious nil votes."
        ),
        "prerequisites": (
            "Control of at least 1/3 of active bonded validators. Technical cost is 0 TIA (no slashing); "
            "the only opportunity cost is block rewards lost during the 60-second jail period."
        ),
        "condition": "1/3 voting power collusion + slash_fraction_downtime=0 (active on mainnet)",
        "example": (
            "Mainnet (2026-05-20, height 11,172,730): slash_fraction_downtime=0, min_signed_per_window=0.001, "
            "signed_blocks_window=10000, downtime_jail_duration=60s."
        ),
        "mitigations": (
            "Currently only slash_fraction_double_sign=0.02 is active; prevote-nil is not a double sign and "
            "therefore not penalized. Recommendations: (1) Introduce nil-vote evidence type (consensus-breaking), "
            "(2) Set slash_fraction_downtime>0 via governance, (3) Explore correlation penalty, "
            "(4) Surface censorship pattern monitoring."
        ),
        "likelihood": "Unrealistic (requires collusion of top 8 institutional validators with no economic incentive)",
        "verification_note": (
            "Phase 1 gap analysis. Slashing parameters cross-source verified against mainnet REST "
            "(celestia-rest.publicnode.com). Code file:line independently re-verified."
        ),
        "da_core_note": (
            "1/3 withholding signatures (prevote-nil) blocks targeted block finalization = "
            "targeted denial of consensus liveness."
        ),
    },
    "CEL-D02": {
        "details": (
            "Due to Celestia's block structure, a single PFB transaction can occupy up to 8 MiB (MaxTxSize), "
            "and only 4 maximum-size PFBs are needed to fill an entire block (BlockMaxBytes=32 MiB). "
            "Transaction inclusion order follows fee/gas-based priority, while shares within the square "
            "are sorted by namespace (go-square builder.go). An attacker can submit large PFBs repeatedly "
            "at minimum gas cost to delay or block normal transactions from being included. While a "
            "MaxPFBMessages cap was introduced in v9, it does not resolve the blockspace monopoly issue itself. "
            "The fee market increases costs as the attack persists, but initial entry cost is low enough "
            "for short-term congestion."
        ),
        "prerequisites": (
            "No barrier to entry beyond TIA gas costs. However, the fee market competition increases "
            "sustained attack costs."
        ),
        "condition": "Attacker can repeatedly submit 8 MiB PFBs by paying only gas costs",
        "example": (
            "Mainnet (2026-05-26): GasPerBlobByte=8, minimum_gas_price=0.002 utia/gas, TIA=$0.468. "
            "One 8 MiB PFB costs ~0.134 TIA (~$0.063), filling entire block (x4) ~$0.25/block, "
            "1 hour sustained (600 blocks) ~$151. Pre-fee-market short-term congestion cost is very low."
        ),
        "mitigations": (
            "Recommendations: (1) Re-weight PFB ordering by fee-per-byte instead of byte-budget, "
            "(2) Weighted cost for large PFBs, (3) Per-user PFB ratio cap."
        ),
        "likelihood": "Conditional (initial cost low, sustained cost rises due to fee market response)",
        "verification_note": (
            "app_consts.go parameters confirmed. Sort criteria in go-square builder.go directly verified "
            "as namespace-ordered -- D02 original claim of byte-budget priority ordering inconsistent with code. "
            "Actual mechanism is low-cost blockspace monopoly by large PFBs under fee/gas priority. "
            "minimum_gas_price on-chain confirmed. Cost calculations verified."
        ),
        "da_core_note": (
            "Blob inclusion delay means DA commitment cannot be obtained, preventing settlement layer "
            "submission and delaying rollup finality. Rollup sequencers using Celestia as DA must submit "
            "DA commitments from Celestia blocks to the settlement layer (e.g., Ethereum) for state updates "
            "to be finalized. Blockspace monopoly-induced inclusion delays temporarily sever this chain. "
            "Since the fee market responds and retries resolve it, this constitutes temporary finality "
            "delay rather than complete service disruption."
        ),
    },
    "CEL-D04": {
        "details": (
            "Three independent defects exist in celestia-core evidence processing, though practical impact "
            "is limited. First, LightClientAttackEvidence.Hash() copies only 31 of 32 bytes, but the "
            "probability of a 248-bit hash collision is effectively 0. Second, consensusBuffer has no cap, "
            "but it drains every block (~6 seconds) and ed25519 signature verification is the CPU bottleneck "
            "(~500-1000/sec), limiting entries to ~3,000-6,000 (~3 MB) within 6 seconds -- OOM is impossible. "
            "Practical impact is minor CPU load. Third, the evidence validity period (~17 days) exceeds "
            "unbonding (14 days) by ~3 days, but double signs are almost certainly detected within 14 days "
            "and tombstoning is the primary penalty, making the 2% slashing avoidance practically meaningless."
        ),
        "prerequisites": (
            "Buffer attack can be attempted with 1 validator but cannot cause OOM. Expiry gap exploitation "
            "requires the unrealistic premise of no evidence submission for 14 days."
        ),
        "condition": "Byzantine validator mass-sending conflicting votes still drains at ~3 MB/block level",
        "example": (
            "Mainnet: evidence.max_age_num_blocks=242,640, max_age_duration=1213200s (337h), "
            "unbonding_time=1213200s. 242640x6s ~ 404h > 337h, so ~17 days vs 14 days."
        ),
        "mitigations": (
            "Recommendations: 1-char fix for evidence.go:325 (tmhash.Size-1 to tmhash.Size), "
            "add per-validator dedup + global cap (e.g., 1000 pairs/height) to consensusBuffer, "
            "change evidence expiry from AND to OR logic or set MaxAgeNumBlocks shorter than unbonding, "
            "add global evidence pool size cap."
        ),
        "likelihood": "Unrealistic (OOM impossible: 6-second drain + CPU bottleneck. Probability of non-detection within 14 days ~0)",
        "verification_note": (
            "Full code audit completed. Evidence/consensus parameters confirmed via mainnet RPC. "
            "All three defects have limited practical impact."
        ),
        "da_core_note": (
            "Claims that consensusBuffer OOM could crash consensus nodes exist, but this is impossible "
            "due to 6-second drain + CPU bottleneck."
        ),
    },
    "CEL-D05": {
        "details": (
            "The ShrEx client (shrex_getter) reads responses using bytes.Buffer.ReadFrom without "
            "io.LimitReader. While the server side applies ReserveMemory, per-peer stream cap, and "
            "rate limits, the client side has no byte ceiling -- only stream deadlines (60-120 seconds). "
            "Four code defects are identified: (1) GetEDS uses an unbounded bytes.Buffer, calling "
            "ReadFrom without io.LimitReader at client.go:142. (2) NamespaceData.ReadFrom collects "
            "frames until EOF with no frame count limit; individual frames have a serde 1 MiB cap but "
            "the number is unlimited. (3) server.go calls Validate() only without Verify(odsSize), "
            "potentially returning abnormal ResponseSize values, but the libp2p resource manager "
            "rejects reservations under default settings so practical impact is nil. (4) bitswap "
            "block_store's Put/PutMany/DeleteBlock/AllKeysChan/HashOnRead panic with 'not implemented', "
            "but these are client receive paths (not serving paths Get/Has/GetSize) on bridge nodes "
            "and are dead code under normal operation."
        ),
        "prerequisites": (
            "Sybil peer infrastructure. However, peers are blacklisted after one failure, "
            "so sustained attacks require many peer IDs."
        ),
        "condition": "Malicious peer must enter victim's peer table, and victim must select that peer for a ShrEx request",
        "example": (
            "Normal maximum EDS size is ~32 MiB (MaxSquareSize=512). At 100 Mbps, malicious streaming "
            "for 60 seconds could cause a ~750 MB transient spike, but with bridge node recommended specs "
            "(8-32 GB), OOM probability is low and GC reclaims immediately."
        ),
        "mitigations": (
            "Existing defenses: stream deadlines (60-120s), peer blacklisting on failure, peer scoring-based "
            "selection, server-side ReserveMemory with rate limit (85 RPS, burst 256). Recommendations: "
            "Apply io.LimitReader(stream, maxResponseSize) on client side, add frame count cap to NamespaceData."
        ),
        "likelihood": "Unrealistic (requires malicious peer in victim's peer table + victim selecting that peer; one-shot then blacklisted; transient memory spike then GC reclaims)",
        "verification_note": (
            "Full code audit completed. All 4 defects are confirmed code-level issues, but existing "
            "defenses (timeout, blacklist, peer scoring, GC) make practical exploitation impossible. "
            "Defensive coding improvement recommended."
        ),
        "da_core_note": (
            "Unrelated to consensus nodes. Only transient memory spike possibility on DA serving nodes; "
            "automatic recovery via existing defenses."
        ),
    },
    "CEL-T01": {
        "details": (
            "Since the shwap protocol transition, BEFP (Bad Encoding Fraud Proof) never functioned, "
            "and it was removed as dead code in PR #4934 on 2026-04-14 (+16/-2398 lines). The current "
            "light node security model relies solely on DAS with 16 samples, verifying only availability "
            "without any data correctness verification. Technically, if a >=2/3 cartel finalizes a "
            "bad-encoded block, light nodes cannot detect it -- but this scenario requires breaking BFT "
            "assumptions and is unrealistic. The real threat lies elsewhere: official documentation "
            "(fraud_proofs.md, CIP-019) still describes 'BEFP + 1-of-N honest full node' as the security "
            "model. Rollup builders trusting this documentation may design systems that depend on Celestia "
            "DA without their own correctness verification. The documentation claiming stronger security "
            "guarantees than reality constitutes a Spoofing threat that poisons downstream security assumptions."
        ),
        "prerequisites": (
            "None. The current state of un-updated documentation is itself the threat. Rollup builders "
            "referencing fraud_proofs.md or CIP-019 may design with incorrect security assumptions."
        ),
        "condition": "Official documentation states a security model (DAS+BEFP) different from the actual model (DAS-only)",
        "example": (
            "PR #4934: 'fraud proofs were never produced or validated post-shwap'. Issue #4930: "
            "'straight-forward removal of dead code'. Reviewer @walldiss: 'Goodbye BEFPs'. go-fraud "
            "archive request (go-fraud#143). Meanwhile fraud_proofs.md still states 'BEFPs enforce DAS'."
        ),
        "mitigations": (
            "Recommendations: (1) Update fraud_proofs.md to document BEFP removal and current DAS-only model, "
            "(2) Correct CIP-019's 'security model unchanged' claim, (3) Document in light node docs that "
            "DAS guarantees availability only, not correctness, (4) Add self-verification recommendation "
            "to rollup integration guide."
        ),
        "likelihood": "Immediate (documentation misrepresentation is currently active and referenceable by rollup builders)",
        "verification_note": (
            "PR #4934 body, merge date, and diff confirmed. Issue #4930 confirmed. Documentation "
            "(fraud_proofs.md, CIP-019) confirmed as un-updated. BEFP removal itself is not a security "
            "change (already non-functional), but documentation not reflecting reality is the core threat."
        ),
        "da_core_note": (
            "Not a direct DA invariant violation but a Spoofing threat. Documentation claims stronger "
            "security guarantees than reality, poisoning rollup builders' security design assumptions. "
            "The 2/3 cartel scenario requires breaking BFT assumptions and is unrealistic; the practical "
            "harm path is stale docs leading to rollup mis-design leading to runtime vulnerabilities."
        ),
    },
    "CEL-E01": {
        "details": (
            "SP1Blobstream's guardian, used by L2 rollups as a finality signal, is a 4-of-6 Gnosis Safe "
            "(0x8bF34D8df1eF0A8A7f27fC587202848E528018E6) where GUARDIAN, TIMELOCK, and DEFAULT_ADMIN "
            "roles are all concentrated on the same multisig (confirmed via 3 on-chain hasRole() calls "
            "and RoleGranted events at block 20027685). Root cause: initialize() passes the same address "
            "to both _timelock and _guardian via __TimelockedUpgradeable_init(guardian, guardian). "
            "Verifier/program vkey replacement functions lack timelock, events, and review windows, "
            "allowing instant upgrade with 4 signer consensus in a single transaction. Additionally, "
            "ProofOutputs lacks chain-id enabling cross-deployment proof reuse, and updateGenesisState "
            "lacks height monotonicity enforcement enabling stale validator set rollback. As of 2026-05-24 "
            "on Etherscan, all 12,109 contract transactions are commitHeaderRange (relayer) calls, "
            "with 0 internal transactions and 0 verifyAttestation calls -- no L2 uses SP1Blobstream "
            "for DA verification on-chain. Molten Network/Rari Chain SequencerInbox's BLOBSTREAM() "
            "getter returns 0xa8973B... which has bytecode 0 (dead pointer, confirmed on Arbiscan)."
        ),
        "prerequisites": (
            "Compromise or coercion of 4 of 6 signers. No immediate impact currently, but blast radius "
            "increases dramatically if Blobstream adoption expands."
        ),
        "condition": "4-of-6 multisig signer compromise + currently no L2 using Blobstream DA bridge, limiting immediate impact",
        "example": (
            "Ethereum mainnet proxy 0x7Cf3876F681Dbb6EdA8f6FfC45D66b996Df08fAe, "
            "guardian=0x8bF34D8df1eF0A8A7f27fC587202848E528018E6 (4-of-6 Gnosis Safe v1.3.0, "
            "singleton 0xd9db...9552), VERSION 1.1.0, checkRelayer true, nonce 11. "
            "6 signer EOAs: 0x0449...56a9, 0x7939...E899, 0x1358...7caf, 0x4587...1b0, "
            "0x4983...cE4d, 0x91D4...e15."
        ),
        "mitigations": (
            "Recommendations: (1) Route updateVerifier/updateProgramVkey through separate TIMELOCK role "
            "with MIN_DELAY + add events, (2) Add require(_height>latestBlock) to updateGenesisState, "
            "(3) Add chain_id+genesis_hash to ProofOutputs, (4) Separate GUARDIAN (freeze) and "
            "TIMELOCK (upgrade) roles."
        ),
        "likelihood": "Conditional (compromise or coercion of 4-of-6 multisig signers)",
        "verification_note": (
            "Phase 2 pen-test (P3) + primary source on-chain verification: (1) eth_call hasRole() 3x "
            "confirmed same address holds all 3 roles, (2) getThreshold()=4, getOwners()=6 EOAs confirmed, "
            "(3) RoleGranted at block 20027685 with 3 roles granted simultaneously, 0 RoleRevoked events, "
            "(4) All 12,109 tx are commitHeaderRange, 0 internal tx confirming 0 L2 DA verification usage, "
            "(5) Molten/Rari BLOBSTREAM() dead pointer confirmed. Multisig address corrected from prior "
            "report error (0xBaB2c...126, 38 hex chars) to actual 0x8bF34D8...18E6."
        ),
        "da_core_note": (
            "L1 bridge trust issue. Outside Celestia DA consensus/signing/recovery invariants. "
            "No immediate impact due to zero L2 usage, but critical if adoption increases."
        ),
    },
    "CEL-S01": {
        "details": (
            "An attacker operating numerous sybil nodes to dominate a specific light node's peer set can "
            "deceive it into believing unavailable data is available. Procedure: (1) Malicious block producer "
            "withholds ~25% of EDS shares from the network, (2) Distributes withheld shares only to sybil "
            "nodes, (3) Replaces target light node's peers with sybils via DHT poisoning, (4) When the "
            "target requests DAS samples, sybils respond to all -- target falsely concludes data is available. "
            "P2P transport is non-anonymous, allowing attackers to identify requesters and provide selective "
            "responses per target. With DefaultSampleAmount=16, even without sybils the per-client deception "
            "probability is ~1%, and with 400 clients the probability of at least one being deceived is "
            "~98.2% (Common Prefix 2022)."
        ),
        "prerequisites": (
            "Sybil node operating costs (N servers), DHT poisoning to dominate target's peer set. "
            "EnableBlackListing defaults to false, so the same sybil can reconnect without being blocked."
        ),
        "condition": "Non-anonymous P2P transport + sybil nodes dominate target light node's peer set",
        "example": (
            "Common Prefix (2022-11-09): 16 samples, 25% withheld results in ~1% per-client deception "
            "probability. With 400 clients, probability of at least one being deceived is ~98.2%."
        ),
        "mitigations": (
            "No defense in current code. Nym anonymous transport integration is in R&D (not deployed). "
            "Recommendations: (1) Accelerate anonymous transport adoption, (2) Enforce peer diversity, "
            "(3) Cross-verify sampling results between light nodes, (4) Change EnableBlackListing default to true."
        ),
        "likelihood": "Low (sybil infrastructure cost is low but block producer collusion is required)",
        "verification_note": (
            "Phase 3 external input cross-check. Common Prefix research paper body confirmed. "
            "k=15 to 16 recalculation correction applied. Actual sybil cluster operating cost "
            "(DHT poisoning) not verified (PARTIAL)."
        ),
        "da_core_note": (
            "Target light node falsely judges unavailable data as available, neutralizing DA verification "
            "for rollups depending on that node."
        ),
    },
    "G-CON-01": {
        "details": (
            "Only 8 validators are needed to reach the 1/3 threshold, and 6 of them are KYC-regulated "
            "financial institutions under US, EU, Swiss, and Hong Kong jurisdictions. A single judicial "
            "order could execute CEL-D01-style prevote-nil censorship legally, without any malicious intent "
            "from validators. Anchorage Digital alone holds 11.08%, immediately alignable via a single "
            "US court order. max_validators=100 with 94 currently bonded effectively blocks new entrants "
            "(validator set saturation). Delegator diversification alone does not reduce the minimum "
            "number of validators needed for the 1/3 threshold."
        ),
        "prerequisites": (
            "Court order or OFAC designation targeting 6-7 KYC entities. Validators comply out of "
            "legal obligation, not malice."
        ),
        "condition": "Judicial order or sanctions designation aligning 1/3 of KYC validators",
        "example": (
            "2026-05-24 mainnet: top-8 cumulative 35.77% (>1/3), top-28 67.02% (>2/3), "
            "Anchorage 11.08%. 94/100 bonded. Total registered 301 (bonded 94 + unbonding 192 + other 15)."
        ),
        "mitigations": (
            "Recommendations: (1) Validator decentralization incentives (support non-KYC validators), "
            "(2) Increase MaxValidators (currently 100), (3) Resolve validator set saturation, "
            "(4) L2/user-side censorship resistance SLA evaluation."
        ),
        "likelihood": "Conditional (court order or OFAC designation targeting 6-7 corporate entities)",
        "verification_note": (
            "Cross-source confirmed across 3 endpoints (publicnode/polkachu/pops.one). "
            "94 bonded, top-8 35.77%, top-28 67.02% structure maintained (2026-05-24)."
        ),
        "da_core_note": (
            "Validator concentration + validator set saturation enables CEL-D01-style "
            "targeted denial of consensus liveness."
        ),
    },
    "G-OPS-01": {
        "details": (
            "Multiple user-facing surfaces including official specs, docs, blog, and CIPs have been "
            "stale for 5+ weeks, promising BEFP, 1-of-N honest full node, and 25% slashing threshold. "
            "The discrepancy is not accidental but a structural pattern: parameter/safety-model change PRs "
            "are not accompanied by docs PRs. This can cause L2 builder finality mis-design and "
            "academic citation errors."
        ),
        "prerequisites": (
            "Not a code exploit. L2 builders/researchers trust stale surfaces and design incorrectly."
        ),
        "condition": "Safety model/parameter change PRs merge without accompanying docs + users trust stale surfaces",
        "example": (
            "Stale surfaces: fraud_proofs.md ('BEFPs enforce DAS'), docs slashing ('25% of 5,000 blocks', "
            "actual is 0.1%/10,000), CIP-019 ('Does not change the security model')."
        ),
        "mitigations": (
            "Recommendations: (1) Make docs PR mandatory for code PRs (block CI without docs PR), "
            "(2) Add deprecation banner to all stale surfaces, (3) Quarterly stale audit."
        ),
        "likelihood": "Structural/non-exploit (social engineering surface)",
        "verification_note": (
            "docs.celestia.org slashing page confirmed stale. Contradiction with mainnet measurement "
            "(0.1%/10,000) confirmed."
        ),
        "da_core_note": "Documentation/process transparency gap. Can cause L2 builder mis-design.",
    },
    "CEL-D10": {
        "details": (
            "server.go's handleDataRequest reserves memory via ResponseSize(edsSize) before responding. "
            "edsSize is looked up from the server's local store rather than from the request. If the block "
            "is not in the store, it returns NOT_FOUND immediately (no memory reservation). If the block "
            "exists but namespace data is empty, it reserves memory for the full ODS size regardless of "
            "actual data size, then returns an empty response. On mainnet with GovMaxSquareSize=128 (ODS), "
            "ResponseSize = 128x128x512 = 8 MiB/stream. Service scope per-peer cap = 2, so a single peer "
            "can trigger 2 concurrent streams for 16 MiB reservation. Empty namespace responses complete "
            "immediately, causing quick reservation release."
        ),
        "prerequisites": "One node with P2P network access. Knowledge of block heights held by the target node.",
        "condition": "P2P peer requests NamespaceData for an empty namespace in an existing block. Service scope limits to 2 streams per peer.",
        "example": (
            "Mainnet GovMaxSquareSize=128 (ODS, on-chain confirmed): edsSize=256, odsLn=128, "
            "ResponseSize=8 MiB/stream. Service scope per-peer cap=2 yields 16 MiB from a single peer. "
            "Empty namespace responses complete immediately, releasing reservations instantly."
        ),
        "mitigations": (
            "Recommendations: (1) Check namespace data size first and reserve based on actual size, "
            "(2) Change ReserveMemory to actual response size-based allocation."
        ),
        "likelihood": "Low (possible with 1 P2P peer but only 16 MiB/peer level, released immediately)",
        "verification_note": (
            "Code verification completed. Confirmed edsSize comes from server local store lookup "
            "(not from request) in server.go. GovMaxSquareSize=128 confirmed via mainnet REST "
            "(celestia-rest.publicnode.com). Service scope per-peer cap=2 confirmed in limits.go."
        ),
        "da_core_note": (
            "Potential to exhaust resource manager budget, but at 16 MiB per peer with immediate "
            "release for empty responses, practical impact is minimal."
        ),
    },
    "CEL-D12": {
        "details": (
            "GetProposal at celestia-core consensus/propagation/commitment_state.go:95 can trigger a "
            "nil pointer dereference panic when getAllState returns cb=nil, has=true. The stored-block "
            "branch of getAllState (line 190-196) returns (nil, cparts, bitarray, true) when the block "
            "exists in BlockStore but not in the proposal cache. The primary caller at "
            "consensus/state.go:2920 discards the first return value (_), so panic does not occur on "
            "most paths. However, the syncData path (state.go:2929) can trigger it, as confirmed in "
            "PR #3060 tests. The function contract itself is broken, creating panic risk for future callers."
        ),
        "prerequisites": (
            "Can occur during normal operation. Intentional trigger: malicious peer induces proposal "
            "request immediately after block store write."
        ),
        "condition": "Block exists in BlockStore but not in proposal cache during sync timing + syncData path entry",
        "example": "getAllState returns (nil, cparts, bitarray, true) causing &cb.Proposal to panic.",
        "mitigations": "PR #3060 (open): adds nil guard. No defense before merge.",
        "likelihood": "Low (triggers only on specific sync timing; primary caller discards return value)",
        "verification_note": (
            "celestia-core main branch commitment_state.go code confirmed. PR #3060 existence "
            "and open status confirmed via gh api."
        ),
        "da_core_note": "Potential for consensus node panic, but only triggers on specific sync paths. PR #3060 adds nil guard.",
    },
    "CEL-D13": {
        "details": (
            "celestia-app's handleBlobCheckTx executes ValidateBlobTx followed by "
            "CreateParallelCommitments before gas deduction. MsgPayForBlobs.ValidateBasic() has no "
            "blob count limit, so a BlobTx containing thousands of 1-byte blobs forces NMT subtree + "
            "Merkle root computation for each blob. If the signature is invalid or fees insufficient, "
            "computation is wasted but gas is not charged. Within the MaxTxSize=8 MiB limit, thousands "
            "of tiny blobs are possible. The ante chain order is: SetUpContext > ... > DeductFee > "
            "SigVerify > MinGasPFB > BlobShare, so commitment computation executes before this chain."
        ),
        "prerequisites": "RPC access. Invalid signature transactions can also force commitment computation.",
        "condition": "Attacker submits BlobTx with many tiny blobs repeatedly",
        "example": (
            "1-byte blob x 1000 = ~70KB tx (including metadata). NMT commitment x 1000 = "
            "significant CPU. Gas ~4M but uncharged with invalid signature."
        ),
        "mitigations": (
            "Recommendations: (1) Add MaxBlobsPerPFB cap to ValidateBasic, (2) Move commitment "
            "computation after signature verification, (3) Early rejection in CheckTx based on blob count."
        ),
        "likelihood": "Immediate (send BlobTx; gas is normally charged but can force computation with invalid tx at zero cost)",
        "verification_note": (
            "celestia-app main branch check_tx.go, blob_tx.go, payforblob.go code confirmed. "
            "Absence of blob count cap in ValidateBasic confirmed."
        ),
        "da_core_note": "Validator CheckTx CPU exhaustion leads to mempool processing delays and consensus throughput degradation.",
    },
    "CEL-D14": {
        "details": (
            "In ProcessProposal, ValidateBlobTxWithCache skips commitment recomputation for blob txs "
            "present in TxCache. A malicious proposer can include blob txs that did not pass other "
            "validators' CheckTx, forcing non-proposer validators to perform full commitment computation. "
            "However, total block data is limited by square size (current ODS 128 -> max ~8 MiB), and "
            "even with MaxPFBMessages=200, total data cannot exceed the square. The original claim of "
            "'200 x 8 MiB = 1.6 GiB' is impossible. Commitment computation is parallelized with "
            "runtime.NumCPU()*2 workers, taking only hundreds of milliseconds for 8 MiB of data."
        ),
        "prerequisites": "One active validator with minimum stake.",
        "condition": "Malicious validator selected as proposer includes uncached blob tx in block proposal. Total data limited by square size.",
        "example": (
            "MaxPFBMessages=200 but total block data is limited to ~8 MiB at ODS 128. "
            "CreateParallelCommitments runs with NumCPU()*2 workers in parallel. "
            "8 MiB commitment computation takes ~hundreds of milliseconds."
        ),
        "mitigations": (
            "Recommendations: (1) Limit uncached tx ratio in ProcessProposal, "
            "(2) Enforce commitment computation timeout, (3) Lightweight pre-verification on TxCache miss."
        ),
        "likelihood": "Low (requires being selected as proposer + actual computation load limited by square size)",
        "verification_note": "process_proposal.go ValidateBlobTxWithCache code confirmed. Full validation path on cache miss confirmed.",
        "da_core_note": (
            "Asymmetry between proposer and validator exists, but square size limits make actual "
            "CPU load minor. No meaningful impact on consensus liveness."
        ),
    },
    "CEL-D15": {
        "details": (
            "The Subscribe method in celestia-node blob/service.go runs an infinite retry loop without "
            "time.Sleep when getAll fails. Unless ctx is cancelled, the pattern "
            "'for { getAll(); if err==nil break }' consumes 100% CPU. If a malicious full node returns "
            "intermittent errors for a specific namespace's data requests, a light node subscribed to "
            "that namespace enters a tight busy-loop."
        ),
        "prerequisites": "One malicious full node that can connect as a peer to the target light node.",
        "condition": "Light node has active subscription for a namespace where peers return intermittent errors",
        "example": (
            "for { blobs, err = s.getAll(ctx, header, []Namespace{ns}); if err == nil { break } } "
            "-- no sleep, no backoff."
        ),
        "mitigations": (
            "Recommendations: (1) Add exponential backoff, (2) Max retry count, "
            "(3) time.Sleep between retries (minimum 100ms)."
        ),
        "likelihood": "Conditional (malicious full node + specific namespace subscriber)",
        "verification_note": "celestia-node main branch blob/service.go Subscribe method code directly confirmed.",
        "da_core_note": "Light node CPU exhaustion stops DAS sampling, disabling DA verification for that node.",
    },
    "CEL-D17": {
        "details": (
            "celestia-app's TxCache stores entries keyed by sha256(inner SDK tx) during CheckTx, "
            "but deletes using sha256(full BlobTx wire bytes) during FinalizeBlock. Since PrepareProposal "
            "re-serializes blob tx via MarshalBlobTx(innerTx, blobs...), FinalizeBlock's req.Txs contain "
            "full BlobTx bytes that differ from inner SDK tx bytes. Therefore sha256(full) != sha256(inner), "
            "and cache deletion always fails. TxCache is based on sync.Map with no cap, TTL, or separate "
            "cleanup path, so entries accumulate indefinitely. Additionally, txCache.Set() executes before "
            "BaseApp.CheckTx() in CheckTx, so rejected transactions with valid blob structure but invalid "
            "nonce/fee/gas also persist in cache. In this case, attack cost is 0 TIA -- leakage occurs "
            "at CheckTx ingress rate without requiring block inclusion."
        ),
        "prerequisites": (
            "RPC or P2P access. The rejected tx path requires no fees. The valid tx path requires "
            "only minimum gas fees."
        ),
        "condition": "Any path that can submit blob txs to a celestia-app node (RPC or P2P)",
        "example": (
            "Directly verified: future sequence blob tx -> checktx_code=32, cache entry persists. "
            "Zero-fee blob tx -> checktx_code=11, cache entry persists. Production path test: "
            "CheckTx then FinalizeBlock(wrappedTx) -> fromCache=true (cache not deleted confirmed). "
            "Per-entry measured memory: ~204 bytes. At 100 Mbps rejected tx rate: ~160 seconds per 1 GB leak."
        ),
        "mitigations": (
            "No current defense. Recommendations: (1) Re-parse blob tx via UnmarshalBlobTx in "
            "FinalizeBlock and delete using inner tx key, (2) Call txCache.Set only after "
            "BaseApp.CheckTx succeeds in CheckTx, (3) Add max size cap or TTL to TxCache."
        ),
        "likelihood": "Immediate (rejected blob tx path: zero cost, requires only RPC/P2P access)",
        "verification_note": (
            "Full code path trace + sha256 hash direct computation + production path reproduction test "
            "written and executed (PASS). Rejected tx cache persistence also execution-verified. "
            "Per-entry memory measured (~204 bytes/entry). Root cause of existing tests not reproducing "
            "production path also identified."
        ),
        "da_core_note": (
            "Validator/consensus node memory exhaustion -> OOM crash -> consensus participation halt. "
            "Irreversible accumulation (no recovery except restart). Simultaneous attack on multiple "
            "validators can cause 1/3 departure -> chain liveness threat."
        ),
    },
    "CEL-D03": {
        "details": (
            "The SHREX peer manager's blacklistedHashes (map[string]bool) has only addition paths and "
            "no deletion paths. shrexsub message validation checks only height!=0, non-empty EDS, and "
            "32-byte hash length without verifying whether the DataHash actually exists on-chain. An "
            "attacker injecting unique fake 32-byte DataHashes causes each to create an unvalidated pool. "
            "After PoolValidationTimeout (2 minutes), cleanUp() deletes the pool but permanently adds "
            "the hash to blacklistedHashes[h]=true. In manager.go, delete() applies only to m.pools; "
            "no delete() for m.blacklistedHashes exists anywhere in the codebase. Bridge nodes do not "
            "use the WithShrexSubPools path (p2p_constructors.go:58), so direct targets are limited "
            "to Light nodes."
        ),
        "prerequisites": (
            "One node with P2P network access. No fees required. Same peer can inject "
            "indefinitely without blocking (see CEL-D06)."
        ),
        "condition": "P2P connection to Light node + repeated unique fake DataHash injection. Peer blocking disabled by default.",
        "example": (
            "Local PoC verified: N unique fake hashes injected -> N unvalidated pools created -> "
            "timeout then cleanUp() -> blacklistedHashes length increases by N, pools deleted but "
            "hashes persist. Defaults: PoolValidationTimeout=2min, GcInterval=30s."
        ),
        "mitigations": (
            "No current defense. Recommendations: (1) Add TTL or max size cap to blacklistedHashes, "
            "(2) Per-peer rate limit on new hash ingestion, (3) Change EnableBlackListing default to "
            "true (CEL-D06), (4) Add header store existence check to shrexsub validation."
        ),
        "likelihood": "Conditional (P2P peer access + repeated unique hash injection; no fee needed; peer blocking disabled by default)",
        "verification_note": (
            "Full code audit completed (commit f8cefbe). Absence of delete() for blacklistedHashes "
            "confirmed. Local unit reproduction completed. Isolated Light node network PoC is feasible "
            "but not executed. Real-world exploitability on public network requires further testing."
        ),
        "da_core_note": (
            "Light node memory exhaustion -> DAS sampling halt -> DA verification disabled for that node. "
            "Bridge nodes are unaffected."
        ),
    },
    "CEL-D06": {
        "details": (
            "The SHREX peer manager's EnableBlackListing defaults to false (options.go:62, TODO comment: "
            "'enable blacklisting once all related issues are resolved'). In blacklistPeers() "
            "(manager.go:416-438), when EnableBlackListing=false, calls to connGater.BlockPeer() and "
            "host.Network().ClosePeer() are skipped. As a result, peers that sent invalid data are only "
            "logged but not actually blocked, allowing them to reconnect immediately or continue attacks "
            "on the existing connection. This default weakens the defense premises of CEL-D03 "
            "(blacklistedHashes unbounded growth), CEL-D05 (ShrEx unbounded response), and CEL-S01 "
            "(DAS Selective Disclosure). CEL-D05 and CEL-S01 cite 'peer blacklisting after one failure' "
            "as an existing defense, but this defense is inoperative under default settings."
        ),
        "prerequisites": (
            "None. The default configuration itself is the threat condition. Malicious peers need only "
            "P2P access to retry indefinitely without being blocked."
        ),
        "condition": "Light node running with celestia-node default settings. EnableBlackListing=false is the default.",
        "example": (
            "Default settings: EnableBlackListing=false, PoolValidationTimeout=2min, GcInterval=30s. "
            "Malicious peer sends fake DataHash -> hash added to blacklistedHashes but peer itself is "
            "not blocked (BlockPeer()/ClosePeer() not called) -> peer retries with new hash."
        ),
        "mitigations": (
            "Recommendations: (1) Change EnableBlackListing default to true, (2) Publish roadmap "
            "for resolving TODO ('all related issues'), (3) Add EnableBlackListing=true recommendation "
            "to operator documentation, (4) Implement per-peer rate limit that works without blacklisting."
        ),
        "likelihood": "Immediate (default configuration is itself the threat; no separate attack action needed)",
        "verification_note": (
            "Code directly confirmed (commit f8cefbe). EnableBlackListing=false default, TODO comment "
            "original text, and blacklistPeers() gating logic all confirmed. Cross-verified that "
            "CEL-D05/S01's 'blacklist defense' claim is inoperative under default settings."
        ),
        "da_core_note": (
            "Not a direct DA invariant violation but defense mechanism disabled. Acts as an enabler "
            "that amplifies the blast radius of CEL-D03/D05/S01."
        ),
    },
    "CEL-P01": {
        "details": (
            "Celestia's double_sign slashing is a flat 2% (slash_fraction_double_sign=0.02), using the "
            "standard Cosmos SDK x/slashing module implementation without a correlation penalty. Whether "
            "1 validator or 28 validators double sign simultaneously, each is slashed exactly 2%. "
            "Ethereum PoS applies a correlation penalty that effectively reaches 100% slashing for "
            "coordinated attacks -- roughly 50x more expensive at equivalent scale. A practical attack "
            "scenario (2/3+ collusion) is unrealistic due to coordination costs (orchestrating 28 "
            "independent entities, whistleblower risk, timing synchronization) and the absence of a "
            "revenue mechanism (double signing itself yields no direct profit). However, this design "
            "choice indicates structurally weaker on-chain deterrence against coordinated safety "
            "violations compared to Ethereum PoS."
        ),
        "prerequisites": (
            "N/A -- no practical attack scenario. Note: top 28 validators (67.02%, ~340.6M TIA) "
            "colluding would face only ~$3.19M in on-chain costs (at TIA $0.468), but coordination "
            "costs and absence of revenue path make this economically irrational."
        ),
        "condition": "N/A -- no clear attack path identified. Classified as a design gap.",
        "example": (
            "Mainnet (2026-05-26): slash_fraction_double_sign=0.02, slash_fraction_downtime=0.0 "
            "(on-chain confirmed), TIA=$0.468 (CoinGecko), top 28 cumulative ~340.6M TIA (67.02%). "
            "Theoretical on-chain cost: ~$3.19M. Comparison: Ethereum PoS coordinated attack -> "
            "~100% slashing (correlation penalty), ~50x cost at equivalent scale."
        ),
        "mitigations": (
            "Recommendations: (1) Introduce correlation penalty to Cosmos SDK (ref EIP-7002), "
            "(2) Raise slash_fraction_double_sign to 10%+ via governance, (3) Implement weighted "
            "slashing for simultaneous multi-validator double signs, (4) Set slash_fraction_downtime>0 "
            "(currently 0, no liveness penalty)."
        ),
        "likelihood": "Unrealistic (2/3 collusion premise + coordination cost > financial gain + no revenue mechanism)",
        "verification_note": (
            "Slashing parameters confirmed directly from celestia-rest.publicnode.com (2026-05-26). "
            "TIA price confirmed via CoinGecko API. Correlation penalty absence confirmed in Cosmos SDK "
            "x/slashing source. slash_fraction_downtime=0 additionally confirmed."
        ),
        "da_core_note": (
            "Common Cosmos SDK design characteristic. A protocol design observation, not a Celestia-specific "
            "vulnerability. No realistic attack potential due to coordination costs and absence of revenue mechanism."
        ),
    },
    "CEL-D11": {
        "details": (
            "The CAT mempool's pendingSeenTracker in celestia-core has a per-signer cap of 128 entries "
            "but no global cap on the number of signers. The reactor.go SeenTx handler accepts msg.Signer "
            "without signature verification but internally queries querySequenceFromApplication(msg.Signer) "
            "to look up the address's expected sequence. If the response sequence is 0 or the query fails "
            "(including new/non-existent accounts), haveExpected=false is returned and pendingSeen.add is "
            "not entered, blocking mass fake signer injection. However, combining actual on-chain account "
            "addresses (sequence>0) with future sequences higher than the current expected sequence creates "
            "pending entries. These entries have no TTL or eviction and persist in the map until the sequence "
            "catches up or the 128th entry for the same signer pushes it out. Since mainnet has many known "
            "accounts (sequence>0), a single peer can recycle known signer lists to inflate the perSigner "
            "map without bound. The TODO comment at reactor.go line 425 directly acknowledges this issue."
        ),
        "prerequisites": (
            "One P2P-connected node. On-chain account address collection (obtainable via chain scanning). "
            "No fees required."
        ),
        "condition": "CAT mempool-enabled node with P2P connection + possession of known on-chain account address list",
        "example": (
            "Known signer A -> seq 999 SeenTx sent -> perSigner[A] entry created. Known signer B -> "
            "seq 999 sent -> perSigner[B] created. N known accounts x 128 slots x entry size -> "
            "GB-scale memory inflation."
        ),
        "mitigations": (
            "PR #3061 (DRAFT, 2026-05-22): adds per-peer cap (10,000) + TTL (2 min) eviction. "
            "Global signer cap not added. No defense before merge."
        ),
        "likelihood": "Conditional (1 P2P peer + known on-chain signer list required)",
        "verification_note": (
            "pending.go directly confirmed: defaultPendingSeenPerSigner=128 (line 11), perSigner map "
            "has no TTL or global signer cap. reactor.go directly confirmed: querySequenceFromApplication "
            "(line 824-837) returns haveExpected=false when resp.Sequence==0 or on error; TODO comment "
            "at line 425 original text confirmed. PR celestia-core#3061 DRAFT status and diff confirmed: "
            "seenTxPerPeerLimit=10,000 (cache.go), pendingSeenTTL=2*time.Minute (pending.go) added; "
            "global signer count cap not added."
        ),
        "da_core_note": "Consensus node OOM -> consensus participation halt -> liveness degradation.",
    },
    # ── Ethereum ──────────────────────────────────────────────
    "ETH-S01": {
        "details": (
            "In go-ethereum/eth/catalyst/api_testing.go L37-44, the `testing_` namespace is configured "
            "with Authenticated:false. If the Engine API port (8551) is exposed to the internet due to "
            "firewall misconfiguration, the testing API becomes accessible without authentication. "
            "This remains active in the Osaka/BPO fork beyond the Fulu fork."
        ),
        "prerequisites": "Engine API port exposed to the internet due to firewall misconfiguration",
        "condition": "Engine port 8551 exposed (firewall misconfigured)",
        "mitigations": "Attack surface eliminated when port 8551 is restricted by firewall. Under normal operation, it binds to localhost.",
        "likelihood": "Low",
        "verification_note": "Confirmed testing_ namespace Authenticated:false in api_testing.go. Only accessible externally when firewall is misconfigured.",
    },
    "ETH-S02": {
        "details": (
            "In PeerDAS, custody group assignment is based on node_id. An attacker can brute-force "
            "generate node_ids that concentrate on specific data column sets, threatening the "
            "availability of those columns. With Fulu fork activating PeerDAS, custody groups become "
            "an actual security boundary, increasing the impact."
        ),
        "prerequisites": "Significant computing resources for brute-force node_id generation",
        "condition": "PeerDAS custody group assignment via node_id",
        "mitigations": "The custody group count is sufficiently large, and grinding cost relative to node count makes practical attack difficulty high.",
        "likelihood": "Low",
        "verification_note": "Confirmed PeerDAS custody group assignment logic is node_id-based in code.",
    },
    "ETH-T01": {
        "details": (
            "In BPO2, updateFraction is set to 11684671. The blob fee calculation formula uses different "
            "denominators depending on the fork. Code paths confirmed and covered by consensus-spec-tests."
        ),
        "prerequisites": "",
        "condition": "",
        "mitigations": "Fork-specific fee calculation formulas are covered by consensus-spec-tests.",
        "likelihood": "Low",
        "verification_note": "Confirmed BPO2 updateFraction=11684671 setting and fork-dependent formula.",
    },
    "ETH-T02": {
        "details": (
            "The KZG trusted setup file is protected by go:embed + sync.Once. An attacker would need "
            "local filesystem access to replace it. Since the file is embedded at build time, runtime "
            "replacement is impossible."
        ),
        "prerequisites": "Access to the build environment or binary distribution chain",
        "condition": "Local filesystem access required",
        "mitigations": "go:embed embeds the file at build time + sync.Once prevents runtime re-initialization.",
        "likelihood": "Low",
        "verification_note": "Confirmed go:embed + sync.Once protection mechanism. Runtime file replacement impossible.",
    },
    "ETH-T03": {
        "details": (
            "In Gloas (future feature), data column inclusion proofs are omitted by design. Gloas is "
            "currently unscheduled, so there is no immediate impact. Re-evaluation required when Gloas "
            "is activated."
        ),
        "prerequisites": "Gloas fork must be scheduled and activated",
        "condition": "When Gloas fork is activated",
        "mitigations": "Currently unscheduled. Proof mechanism implementation required before activation.",
        "likelihood": "Low",
        "verification_note": "Gloas-related code paths confirmed. Currently unscheduled.",
    },
    "ETH-T04": {
        "details": (
            "recover_cells_and_kzg_proofs checks for num_cells > CELLS_PER_EXT_BLOB, but "
            "verify_cell_kzg_proof_batch does not perform this check. With Fulu making cell operations "
            "the primary path, bounds check consistency becomes more important from a defense-in-depth "
            "perspective."
        ),
        "prerequisites": "Construction of input that bypasses bounds check",
        "condition": "Abnormal cell index input to verify_cell_kzg_proof_batch",
        "mitigations": "recover_cells_and_kzg_proofs performs preceding check. Upper layer validation filters abnormal inputs.",
        "likelihood": "Low",
        "verification_note": "Confirmed bounds check asymmetry between recover_cells_and_kzg_proofs and verify_cell_kzg_proof_batch.",
    },
    "ETH-T05": {
        "details": (
            "Analysis of column proof verification mechanism in Gloas. Gloas is currently unscheduled "
            "with no immediate impact. Verification logic re-evaluation required upon activation."
        ),
        "prerequisites": "Gloas fork must be scheduled and activated",
        "condition": "When Gloas fork is activated",
        "mitigations": "Currently unscheduled. Verification mechanism must be complete before activation.",
        "likelihood": "Low",
        "verification_note": "Gloas-related code paths confirmed. Currently unscheduled.",
    },
    "ETH-R01": {
        "details": (
            "When a blob or data column with different content for the same (slot, index) pair is "
            "received, the second message is IGNORE-processed without generating slashing evidence. "
            "No mechanism exists to detect equivocation and preserve evidence. With Fulu making data "
            "columns the primary path, equivocation detection importance increases."
        ),
        "prerequisites": "Malicious proposer distributing different blobs/columns for the same slot",
        "condition": "Different content blob/data column received for same (slot, index)",
        "mitigations": "Currently only IGNORE processing. Slashing evidence generation mechanism not implemented.",
        "likelihood": "Low",
        "verification_note": "Confirmed IGNORE-only processing on equivocation, with no slashing evidence generation.",
    },
    "ETH-D01": {
        "details": (
            "In go-ethereum blobpool.go L86, maxTxsPerAccount=16 limits per-account submissions. "
            "Analysis of blobpool exhaustion attacks using minimum 1-Wei fee. Already mitigated by "
            "EIP-7918 fee floor and fee-based eviction."
        ),
        "prerequisites": "Valid Ethereum account with minimum gas fee",
        "condition": "Mass submission of low-cost blob txs to blobpool",
        "mitigations": "maxTxsPerAccount=16 limit, EIP-7918 fee floor, and fee-based eviction.",
        "likelihood": "Low",
        "verification_note": "Confirmed blobpool.go maxTxsPerAccount=16. Mitigated by EIP-7918 fee floor + fee-based eviction. PoC execution confirmed.",
    },
    "ETH-D02": {
        "details": (
            "In Lighthouse overflow_lru_cache.rs L1360-1396, when data column reconstruction fails, "
            "a single bad column causes all 64+ already-verified valid columns to be discarded, "
            "requiring O(N/2) scale re-download. With Fulu making reconstruction the core DA mechanism "
            "(primary path), impact is elevated."
        ),
        "prerequisites": "Malicious peer intentionally propagating bad data columns",
        "condition": "One or more bad columns present during data column reconstruction",
        "mitigations": "LRU cache eviction provides memory bounding. However, no mechanism to preserve verified columns exists.",
        "likelihood": "Medium",
        "verification_note": "Confirmed in Lighthouse overflow_lru_cache.rs that reconstruction failure discards all columns. PRIMARY PATH in Fulu.",
    },
    "ETH-E01": {
        "details": (
            "Lighthouse deletes all columns on reconstruction failure, while Prysm marks reconstructed "
            "columns as verified without re-verification. This cross-client behavioral inconsistency "
            "can cause network-level consensus issues. With Fulu making reconstruction the core DA "
            "mechanism (primary path), impact is elevated."
        ),
        "prerequisites": "Receipt of bad data columns that trigger reconstruction failure",
        "condition": "Data column reconstruction failure occurs",
        "mitigations": "Each client handles failure independently. However, cross-client consistency is absent.",
        "likelihood": "Medium",
        "verification_note": (
            "LH: deletes all columns. Prysm: marks reconstructed columns as verified without "
            "re-verification. PRIMARY PATH in Fulu -- reconstruction is a core DA mechanism."
        ),
    },
}

# ── Repo maps for reference parsing ───────────────────────────

CELESTIA_REPOS = {
    "celestia-core": "celestiaorg/celestia-core",
    "celestia-node": "celestiaorg/celestia-node",
    "celestia-app": "celestiaorg/celestia-app",
    "go-square": "celestiaorg/go-square",
    "rsmt2d": "celestiaorg/rsmt2d",
    "nmt": "celestiaorg/nmt",
    "sp1-blobstream": "succinctlabs/sp1-blobstream",
    "blobstream-contracts": "succinctlabs/blobstream-contracts",
    "CIPs": "celestiaorg/CIPs",
}

ETHEREUM_REPOS = {
    "go-ethereum": "ethereum/go-ethereum",
    "consensus-specs": "ethereum/consensus-specs",
    "c-kzg-4844": "ethereum/c-kzg-4844",
    "lighthouse": "sigp/lighthouse",
    "prysm": "prysmaticlabs/prysm",
    "EIPs": "ethereum/EIPs",
}


def _code_to_github(code_ref: str, repo_map: dict) -> str:
    """Convert a code reference to a GitHub URL. Returns empty string if can't parse."""
    m = re.match(r"([a-zA-Z0-9_-]+)/(.+?)(?::(\d+)(?:-(\d+))?)?(?:\s|$)", code_ref)
    if not m:
        return ""
    repo_short = m.group(1)
    path = m.group(2)
    line_start = m.group(3)
    line_end = m.group(4)
    org_repo = repo_map.get(repo_short)
    if not org_repo:
        return ""
    branch = "master" if repo_short == "go-ethereum" else "main"
    url = f"https://github.com/{org_repo}/blob/{branch}/{path}"
    if line_start:
        url += f"#L{line_start}"
        if line_end:
            url += f"-L{line_end}"
    return url


def parse_references(refs_str: str, repo_map: dict) -> str:
    """Parse references string into formatted markdown."""
    if not refs_str or not refs_str.strip():
        return "*No specific code references provided.*"

    parts = re.split(
        r",\s*(?=(?:code:|onchain:|pr:|issue:|doc:|research:|source:|commit:|test:))",
        refs_str,
    )
    lines = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith("code:"):
            code_ref = part[5:]
            link = _code_to_github(code_ref, repo_map)
            if link:
                lines.append(f"- [`{code_ref}`]({link})")
            else:
                lines.append(f"- `{code_ref}`")

        elif part.startswith("pr:"):
            pr_ref = part[3:]
            m = re.match(r"([a-zA-Z0-9_-]+)#(\d+)\s*(.*)", pr_ref)
            if m:
                repo_short, pr_num, desc = m.group(1), m.group(2), m.group(3).strip(" ()")
                org_repo = repo_map.get(repo_short, f"unknown/{repo_short}")
                url = f"https://github.com/{org_repo}/pull/{pr_num}"
                label = f"PR #{pr_num}"
                lines.append(f"- [{label}: {desc}]({url})" if desc else f"- [{label}]({url})")
            else:
                lines.append(f"- PR: {pr_ref}")

        elif part.startswith("issue:"):
            issue_ref = part[6:]
            m = re.match(r"([a-zA-Z0-9_-]+)#(\d+)\s*(.*)", issue_ref)
            if m:
                repo_short, issue_num, desc = m.group(1), m.group(2), m.group(3).strip(" ()")
                org_repo = repo_map.get(repo_short, f"unknown/{repo_short}")
                url = f"https://github.com/{org_repo}/issues/{issue_num}"
                label = f"Issue #{issue_num}"
                lines.append(f"- [{label}: {desc}]({url})" if desc else f"- [{label}]({url})")
            else:
                lines.append(f"- Issue: {issue_ref}")

        elif part.startswith("doc:"):
            doc_ref = part[4:]
            link = _code_to_github(doc_ref, repo_map)
            if link:
                lines.append(f"- [Doc: `{doc_ref}`]({link})")
            else:
                lines.append(f"- Doc: `{doc_ref}`")

        elif part.startswith("onchain:"):
            lines.append(f"- On-chain: `{part[8:]}`")

        elif part.startswith("research:"):
            research_ref = part[9:]
            url_m = re.search(r"(https?://\S+)", research_ref)
            if url_m:
                url = url_m.group(1).rstrip(")")
                desc = research_ref.replace(url_m.group(0), "").strip(" ,")
                lines.append(f"- [{desc}]({url})" if desc else f"- [Research]({url})")
            else:
                lines.append(f"- Research: {research_ref}")

        elif part.startswith("source:"):
            lines.append(f"- Source: {part[7:]}")

        elif part.startswith("commit:"):
            lines.append(f"- Commit: `{part[7:]}`")

        elif part.startswith("test:"):
            test_ref = part[5:]
            link = _code_to_github(test_ref, repo_map)
            if link:
                lines.append(f"- [Test: `{test_ref}`]({link})")
            else:
                lines.append(f"- Test: `{test_ref}`")

        else:
            lines.append(f"- {part}")

    return "\n".join(lines) if lines else "*No specific code references provided.*"


# ── Page generators ────────────────────────────────────────────


def generate_celestia_page(threat: dict) -> str:
    sid = threat["SID"]
    title = TITLES.get(sid, threat["description"])
    tr = TR.get(sid, {})
    letter, stride_name = stride_from_sid(sid)
    severity = threat.get("severity", "Unknown")
    scope = threat.get("scope", "")
    verification_status = threat.get("verification_status", "")
    core_invariants = threat.get("core_invariants", [])

    details = tr.get("details", threat.get("details", ""))
    prerequisites = tr.get("prerequisites", threat.get("prerequisites", ""))
    condition = tr.get("condition", threat.get("condition", ""))
    example = tr.get("example", threat.get("example", ""))
    mitigations = tr.get("mitigations", threat.get("mitigations", ""))
    likelihood = tr.get("likelihood", threat.get("Likelihood Of Attack", ""))
    verification_note = tr.get("verification_note", threat.get("verification_note", ""))
    da_core_note = tr.get("da_core_note", threat.get("da_core_note", ""))
    verified_by_poc = threat.get("verified_by_poc", [])

    md = []
    md.append(f"# {sid}: {title}\n")
    md.append('{% hint style="info" %}')
    md.append(
        f"**Severity**: {severity} · **STRIDE**: {letter} ({stride_name}) "
        f"· **Scope**: {scope} · **Status**: {verification_status}"
    )
    md.append("{% endhint %}\n")

    md.append("## Overview\n")
    md.append(f"{details}\n")

    if core_invariants or da_core_note:
        md.append("## Core Invariants Affected\n")
        if core_invariants:
            md.append(", ".join(f"`{inv}`" for inv in core_invariants) + "\n")
        if da_core_note:
            md.append(f"{da_core_note}\n")

    md.append("## Prerequisites\n")
    md.append(f"{prerequisites if prerequisites else '*None specified.*'}\n")

    md.append("## Attack Scenario\n")
    if condition:
        md.append(f"**Condition**: {condition}\n")
    if example:
        md.append(f"**Example**: {example}\n")

    md.append("## Impact\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| Severity | {severity} |")
    md.append(f"| Likelihood | {likelihood} |")
    md.append(f"| Scope | {scope} |")
    md.append(f"| Target | {', '.join(threat.get('target', []))} |")
    if core_invariants:
        md.append(f"| Core Invariants | {', '.join(core_invariants)} |")
    md.append("")

    md.append("## Code References\n")
    md.append(parse_references(threat.get("references", ""), CELESTIA_REPOS) + "\n")

    md.append("## Verification & Evidence\n")
    md.append(f"**Status**: {verification_status}\n")
    if verification_note:
        md.append(f"{verification_note}\n")
    if verified_by_poc:
        md.append("**PoC References**:\n")
        for poc in verified_by_poc:
            md.append(f"- {poc}")
        md.append("")

    md.append("## Mitigations\n")
    md.append(f"{mitigations if mitigations else '*No mitigations specified.*'}\n")

    return "\n".join(md)


def generate_ethereum_page(threat: dict) -> str:
    sid = threat["SID"]
    title = TITLES.get(sid, threat["description"])
    tr = TR.get(sid, {})
    letter, stride_name = stride_from_sid(sid)
    bvss_score = threat.get("bvss_score", "N/A")
    bvss_severity = threat.get("bvss_severity", "Unknown")
    bvss_vector = threat.get("bvss_vector", "")
    scope = threat.get("scope", "")
    verification_status = threat.get("verification_status", "")

    details = tr.get("details", threat.get("details", ""))
    prerequisites = tr.get("prerequisites", threat.get("prerequisites", ""))
    condition = tr.get("condition", threat.get("condition", ""))
    example = tr.get("example", threat.get("example", ""))
    mitigations = tr.get("mitigations", threat.get("mitigations", ""))
    likelihood = tr.get("likelihood", threat.get("Likelihood Of Attack", ""))
    verification_note = tr.get("verification_note", threat.get("verification_note", ""))

    md = []
    md.append(f"# {sid}: {title}\n")
    md.append('{% hint style="info" %}')
    md.append(
        f"**Severity**: {bvss_severity} ({bvss_score}/10) · **STRIDE**: {letter} ({stride_name}) "
        f"· **Scope**: {scope} · **Status**: {verification_status}"
    )
    md.append("{% endhint %}\n")

    md.append("## Overview\n")
    md.append(f"{details}\n")

    md.append("## Prerequisites\n")
    md.append(f"{prerequisites if prerequisites else '*None specified.*'}\n")

    md.append("## Attack Scenario\n")
    if condition:
        md.append(f"**Condition**: {condition}\n")
    if example:
        md.append(f"**Example**: {example}\n")
    if not condition and not example:
        md.append("*No specific attack scenario detailed.*\n")

    md.append("## Impact\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| BVSS Score | {bvss_score}/10 ({bvss_severity}) |")
    if bvss_vector:
        md.append(f"| BVSS Vector | `{bvss_vector}` |")
    md.append(f"| Likelihood | {likelihood} |")
    md.append(f"| Scope | {scope} |")
    md.append(f"| Target | {', '.join(threat.get('target', []))} |")
    md.append("")

    md.append("## Code References\n")
    md.append(parse_references(threat.get("references", ""), ETHEREUM_REPOS) + "\n")

    md.append("## Verification & Evidence\n")
    md.append(f"**Status**: {verification_status}\n")
    if verification_note:
        md.append(f"{verification_note}\n")

    md.append("## Mitigations\n")
    md.append(f"{mitigations if mitigations else '*No mitigations specified.*'}\n")

    return "\n".join(md)


# ── Main ───────────────────────────────────────────────────────


def main():
    with open(CELESTIA_JSON, encoding="utf-8") as f:
        celestia_threats = json.load(f)
    with open(ETHEREUM_JSON, encoding="utf-8") as f:
        ethereum_threats = json.load(f)

    os.makedirs(CELESTIA_OUT, exist_ok=True)
    os.makedirs(ETHEREUM_OUT, exist_ok=True)

    cel_count = 0
    for threat in celestia_threats:
        sid = threat["SID"]
        filename = sid_to_filename(sid)
        filepath = os.path.join(CELESTIA_OUT, filename)
        content = generate_celestia_page(threat)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        cel_count += 1
        print(f"  [celestia]  {filename}")

    eth_count = 0
    for threat in ethereum_threats:
        sid = threat["SID"]
        filename = sid_to_filename(sid)
        filepath = os.path.join(ETHEREUM_OUT, filename)
        content = generate_ethereum_page(threat)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        eth_count += 1
        print(f"  [ethereum]  {filename}")

    total = cel_count + eth_count
    print(f"\nDone: {cel_count} Celestia + {eth_count} Ethereum = {total} total pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
