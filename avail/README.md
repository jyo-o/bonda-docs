# Avail

{% hint style="info" %}
**How to Read This Section**

Each finding listed below has its own dedicated page with full technical details, on-chain evidence, and attack scenarios. Click any SID to dive deeper.

- Each finding is sorted into one of four [classification](../methodology/classification.md) tiers — Vulnerability, Operational Risk, Governance Observation, or Design Note. Only Vulnerabilities carry a [CVSS 3.1](../methodology/cvss.md) score; the other tiers are qualitative and feed the [5-axis model](../methodology/scoring.md).
- Verification status indicates whether the finding was confirmed through on-chain probing, source code review, or mainnet fork testing. Learn more about our [verification methodology](../methodology/verification.md).
{% endhint %}

## What is Avail?

Avail is a standalone blockchain purpose-built for data availability, meaning it exists so that other chains can cheaply post their transaction data and prove that data is actually available.

When a rollup submits data to Avail, validators order and commit to that data using **KZG polynomial commitments**. These commitments act as compact cryptographic proofs: anyone can verify the data is correct without downloading all of it. Light clients on the Avail network then perform **Data Availability Sampling**, randomly checking small pieces of the data to confirm nothing was withheld. This means even a lightweight device running a light client can independently verify availability without trusting validators.

To connect Avail's guarantees back to Ethereum, a component called **VectorX** acts as a bridge relayer. It takes Avail's validator commitments, generates a **zero-knowledge proof** using the SP1 proving system, and posts that proof to an Ethereum smart contract. Ethereum-based rollups can then check this contract to confirm that their data was properly committed on Avail.

Avail is built on **Substrate** and uses **Nominated Proof-of-Stake** for consensus, where nominators back validators with their staked AVAIL tokens. Block production uses BABE and finality is achieved through GRANDPA. The KZG trusted setup comes from the Filecoin Powers of Tau ceremony. The AVAIL token itself lives on Ethereum, with mint and burn authority held by the Bridge contract.

## Architecture

![Avail Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/avail-architecture.svg)

## Data Flow

The diagrams below trace how data moves through Avail — the write path that commits rollup data and bridges it to Ethereum, and the read path where light clients verify availability through sampling.

![Avail data flow — write path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/dfd/avail-write.png)

*Write: L2 Batcher submit → Mempool → BABE block production → Erasure + KZG encoding → GRANDPA finality → VectorX Relayer → SP1 Prover → Ethereum L1.*

![Avail data flow — read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/dfd/avail-read.png)

*Read: Full Node header → Sample Planner → DHT/RPC Fetch → KZG Verifier → Confidence accumulation → L2 Contract.*

## System Components

| Component | Role | Trust Level |
|-----------|------|-------------|
| **Avail DA Chain** | Orders transaction data and produces KZG commitments | Decentralized — NPoS with 105 active validators, Nakamoto coefficient ~34 |
| **Light Clients** | Sample random data chunks to verify availability | Trustless — anyone can run one |
| **VectorX** | Relays Avail commitments to Ethereum via ZK proofs | Single relayer EOA — centralized, no on-chain heartbeat |
| **SP1 Verifier Gateway** | Verifies ZK proofs of Avail state on Ethereum | Smart contract controlled by 2/3 multisig |
| **Bridge Contract** | Mints/burns AVAIL token, verifies attestations | Upgradeable with 24h timelock, controlled by 4/7 multisig |
| **AVAIL Token** | ERC-20 on Ethereum, ~791M supply | Immutable contract, mint/burn only via Bridge |
| **TimelockController** | Enforces 24h delay on Bridge upgrades | 86,400s delay, proposer/executor = Governance Multisig |
| **Governance Multisig** | Controls Bridge and VectorX upgrades | 4/7 Gnosis Safe |
| **Pauser Multisig** | Emergency pause capability | 3/5 Gnosis Safe — 4 of 5 owners overlap with Governance |
| **Technical Committee** | Runtime upgrades on Avail chain | 5/7 consensus required |

## Key Numbers

| Metric | Value |
|--------|-------|
| Total findings | 12 |
| Verification status | 9 verified, 3 poc_verified |
| Highest severity | High (CVSS 8.5) |
| Active validators | 105 out of 1,200 max |
| Nakamoto coefficient | ~34 validators to control 33% of stake |
| Governance multisig | 4/7 Gnosis Safe |
| Bridge upgrade delay | 24 hours |
| VectorX upgrade delay | None — instant with 4/7 multisig |

## Threat Summary

12 findings identified through on-chain verification, source code analysis, and Anvil mainnet fork testing. Only Vulnerabilities carry a CVSS 3.1 score.

| SID | Threat | Category | Severity | Status |
|-----|--------|----------|----------|--------|
| [AVL-01](threats/avl-01.md) | MultiAddress::Index Signing Causes Silent Bridge Proof Omission | Vulnerability | High (8.5) | poc_verified |
| [AVL-02](threats/avl-02.md) | Proxy-Wrapped submitData Bypasses DA Extraction | Vulnerability | High (7.7) | poc_verified |
| [AVL-03](threats/avl-03.md) | Kate RPC Unauthenticated KZG Computation | Vulnerability | Medium (5.3) | poc_verified |
| [AVL-04](threats/avl-04.md) | Single Relayer Creates Bridge-Wide SPOF | Operational Risk | High | verified |
| [AVL-05](threats/avl-05.md) | VectorX Upgradeable Instantly Without Timelock | Operational Risk | Medium | verified |
| [AVL-06](threats/avl-06.md) | Deployer EOA Retains Admin Role on VectorX | Governance Observation | — | verified |
| [AVL-07](threats/avl-07.md) | SP1VerifierGateway Route Manipulation via Multisig | Governance Observation | — | verified |
| [AVL-08](threats/avl-08.md) | Key Holder Overlap Across Three Multisigs | Governance Observation | — | verified |
| [AVL-09](threats/avl-09.md) | Unlimited Token Minting via Bridge or VectorX Upgrade | Governance Observation | — | verified |
| [AVL-10](threats/avl-10.md) | Low Validator Utilization Concentrates Power | Design Note | — | verified |
| [AVL-11](threats/avl-11.md) | Slashing Infrastructure Present but Never Triggered | Design Note | — | verified |
| [AVL-12](threats/avl-12.md) | Incomplete Block Reconstruction Limits DAS | Design Note | — | verified |

## Key Findings

### Index-Addressed Submissions Are Silently Dropped from Bridge Proofs

**AVL-01** | Vulnerability, High (8.5)

When a `submit_data` extrinsic is signed through a `MultiAddress::Index` origin, the caller resolves to `None` and the data leaf is dropped from the bridge proof while the submission still succeeds on-chain. An Ethereum-side consumer reconstructing the bridge root never sees the data, so a submission that looks committed on Avail is absent from what the bridge attests to. This is an integrity gap against the data-availability guarantee.

### Proxy-Wrapped Submissions Bypass DA Extraction

**AVL-02** | Vulnerability, High (7.7)

Wrapping `submit_data` in `Proxy::proxy` with `AppId(0)` emits a successful `DataSubmitted` event while the data is never placed in the Kate commitment. Two defects combine: the recursive proxy guard lacks the `submit_data` block its batch counterpart enforces, and the transaction filter drops extraction for any wrapped call at depth greater than zero. Any account can produce data that appears committed but cannot be proven available.

### VectorX Runs on a Single Relayer

**AVL-04** | Operational Risk, High

The entire bridge between Avail and Ethereum depends on a single relayer wallet. There is no backup relayer, no on-chain heartbeat monitoring, and no staleness detection. If this one wallet goes offline or its private key is compromised, DA attestation bridging to Ethereum stops completely. The relay interval is controlled purely on the client side with no on-chain enforcement, and there is no mechanism to propose replacement relayers through the contract. Tracked as an operational indicator, not a structural deduction.

### Deployer EOA Still Has Full Admin Access

**AVL-06** | Governance Observation

The deployer wallet that originally set up the VectorX contract still holds the most powerful admin role. The revocation code was found commented out in the deployment script. Because this admin role governs all other roles, the deployer can grant itself upgrade permissions and replace the entire VectorX contract in just two transactions, bypassing the 4/7 multisig governance entirely. This is recorded against the Decentralization baseline and carries no score.

