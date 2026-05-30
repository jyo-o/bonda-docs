# Avail

{% hint style="info" %}
**How to Read This Section**

Each threat listed below has its own dedicated page with full technical details, on-chain evidence, and attack scenarios. Click any threat ID to dive deeper.

- Threats are scored using [CVSS 3.1](../methodology/cvss.md), the industry-standard vulnerability scoring system.
- Verification status indicates whether the threat was confirmed through on-chain probing, source code review, or mainnet fork testing. Learn more about our [verification methodology](../methodology/verification.md).
{% endhint %}

## What is Avail?

Avail is a standalone blockchain purpose-built for data availability, meaning it exists so that other chains can cheaply post their transaction data and prove that data is actually available.

When a rollup submits data to Avail, validators order and commit to that data using **KZG polynomial commitments**. These commitments act as compact cryptographic proofs: anyone can verify the data is correct without downloading all of it. Light clients on the Avail network then perform **Data Availability Sampling**, randomly checking small pieces of the data to confirm nothing was withheld. This means even a lightweight device running a light client can independently verify availability without trusting validators.

To connect Avail's guarantees back to Ethereum, a component called **VectorX** acts as a bridge relayer. It takes Avail's validator commitments, generates a **zero-knowledge proof** using the SP1 proving system, and posts that proof to an Ethereum smart contract. Ethereum-based rollups can then check this contract to confirm that their data was properly committed on Avail.

Avail is built on **Substrate** and uses **Nominated Proof-of-Stake** for consensus, where nominators back validators with their staked AVAIL tokens. Block production uses BABE and finality is achieved through GRANDPA. The KZG trusted setup comes from the Filecoin Powers of Tau ceremony. The AVAIL token itself lives on Ethereum, with mint and burn authority held by the Bridge contract.

## Architecture

![Avail Architecture](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/assets/avail-architecture.svg)

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
| Total threats identified | 14 |
| Verified | 12 |
| Unverified | 2 |
| Highest severity | High — 8.4, deployer retains admin role on VectorX |
| Active validators | 105 out of 1,200 max |
| Nakamoto coefficient | ~34 validators to control 33% of stake |
| Governance multisig | 4/7 Gnosis Safe |
| Bridge upgrade delay | 24 hours |
| VectorX upgrade delay | None — instant with 4/7 multisig |

## Threat Summary

14 threats identified through on-chain verification, source code analysis, and Anvil mainnet fork testing. All threats are scored using CVSS 3.1.

| SID | Threat | Severity | Status |
|-----|--------|----------|--------|
| [AVL-E03](threats/avl-e03.md) | Deployer EOA retains admin role, can upgrade VectorX solo | High (8.2) | verified |
| [AVL-D01](threats/avl-d01.md) | VectorX single relayer with no on-chain heartbeat or rate limit | High (7.5) | verified |
| [AVL-E04](threats/avl-e04.md) | Technical Committee can upgrade runtime with 5/7 consensus | Medium (6.7) | verified |
| [AVL-D02](threats/avl-d02.md) | Only 105 of 1,200 validator slots are active | Medium (5.9) | verified |
| [AVL-T05](threats/avl-t05.md) | KZG trusted setup relies on Filecoin Powers of Tau ceremony | Medium (5.9) | unverified |
| [AVL-T01](threats/avl-t01.md) | VectorX upgradeable instantly by 4/7 multisig, no timelock | Medium (5.6) | verified |
| [AVL-E01](threats/avl-e01.md) | SP1 Verifier Gateway controlled by 2/3 multisig | Medium (4.0) | verified |
| [AVL-T03](threats/avl-t03.md) | AVAIL token unlimited mint possible via Bridge or VectorX upgrade | Medium (4.0) | verified |
| [AVL-T04](threats/avl-t04.md) | Guardian can inject commitments without ZK proof verification | Medium (4.0) | verified |
| [AVL-P02](threats/avl-p02.md) | Block reconstruction incomplete, DAS guarantee is theoretical | Low (3.7) | unverified |
| [AVL-E02](threats/avl-e02.md) | Key holder overlap across Governance, Pauser, and SP1 multisigs | Low (2.9) | verified |
| [AVL-P01](threats/avl-p01.md) | Slashing exists but has never been triggered in 688 eras | Low (2.1) | verified |
| [AVL-T02](threats/avl-t02.md) | Bridge has 24h timelock, relatively safe upgrade path | Low (1.8) | verified |
| [AVL-S01](threats/avl-s01.md) | TimelockedUpgradeable contract name is misleading, contains no timelock | Informational (0.0) | verified |

## Key Findings

### Deployer EOA Still Has Full Admin Access

**AVL-E03** | High (8.4)

The deployer wallet that originally set up the VectorX contract still holds the most powerful admin role. This role was supposed to be revoked after deployment, but the revocation code was found commented out in the deployment script. Because this admin role governs all other roles, the deployer can grant itself upgrade permissions and replace the entire VectorX contract in just two transactions. This bypasses the 4/7 multisig governance entirely, meaning a single compromised key could take over the bridge.

### VectorX Runs on a Single Relayer

**AVL-D01** | Medium (6.6)

The entire bridge between Avail and Ethereum depends on a single relayer wallet. There is no backup relayer, no on-chain heartbeat monitoring, and no staleness detection. If this one wallet goes offline or its private key is compromised, DA attestation bridging to Ethereum stops completely. The relay interval is controlled purely on the client side with no on-chain enforcement, and there is no mechanism to propose replacement relayers through the contract.

### Validator Set is Underutilized

**AVL-D02** | Medium (5.3)

Avail supports up to 1,200 validators but only 105 are currently active, using just 8.75% of the available capacity. The Nakamoto coefficient is approximately 34, meaning an attacker would need to compromise or collude with 34 validators to control a third of the stake. On the positive side, Avail's NPoS Phragmen election algorithm achieves remarkably even stake distribution: the ratio between the largest and smallest validator stake is only 1.2x.

### Multisig Key Holders Overlap Across Three Groups

**AVL-E02** | Low (0.5)

Three separate multisig wallets govern different parts of the system: Governance, Pauser, and SP1 Verifier. However, these are not truly independent. Four of the five Pauser multisig owners are the same people as Governance multisig owners, and one address appears in all three multisigs. This means compromising the Governance multisig effectively compromises the Pauser and partially compromises the SP1 verifier control as well.

### VectorX Contract Name Implies Timelock That Does Not Exist

**AVL-S01** | Informational (0.0)

VectorX inherits from a contract called `TimelockedUpgradeable`, which suggests upgrades are delayed by a timelock. In reality, this contract contains no delay logic, no queue-and-execute pattern, and no waiting period. The `onlyTimelock` modifier simply checks if the caller has the right role. This naming creates a false sense of security for anyone reviewing the code. The Bridge contract, by contrast, does have a real 24-hour timelock enforced by a separate TimelockController.
