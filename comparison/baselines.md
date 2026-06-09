# Structural Baselines

This page is **track 1 of three**. BONDA does not collapse structural design, exploit severity, and live operations into one synthetic score — they are different classes of evidence, so we show them side by side:

1. **Structural baselines** (this page) — what each DA layer's architecture structurally guarantees, scored against a fixed rubric.
2. **[Vulnerability burden](vulnerability-burden.md)** — the open, exploitable code defects each layer currently carries.
3. **Live signals** (dashboard) — operational health from live feeds.

This page makes the structural baseline **reproducible**. The per-sub-property levels and their primary-source evidence are published here so any reviewer can check or contest them.

> No subtraction happens on this page. Open vulnerabilities are **not** deducted from these baselines; they are reported separately in [Vulnerability burden](vulnerability-burden.md). A baseline answers "what does the architecture guarantee?", not "what is broken right now?".

***

## How to read this page

Each of the five axes (Retrievability, Verifiability, Liveness, Decentralization, Cost Efficiency) is decomposed into three sub-properties. Each sub-property is scored on an integer **0–3** scale against an **observable anchor** — a condition checkable from primary sources, not an adjective:

- **0** — property absent or fundamentally broken
- **1** — exists but with significant structural limitation
- **2** — implemented with minor gaps / not yet production-demonstrated
- **3** — fully implemented and production-verified

A level is set only from structural sources: a Design Note, a Governance Observation, a specification, or an on-chain query, per the anchors in [5-Axis Risk Scoring](../methodology/scoring.md). Operational conditions and live performance are reported on the dashboard, not here. Every level carries its source and is **contestable with evidence**. Where the published material gives no basis for a sub-property, the cell reads `—` and the axis band is computed only on the scored cells.

The three sub-property levels roll up to a qualitative **axis band** (we report a band, not a false-precise decimal):

| Sum of 3 levels (0–9) | Axis band |
|---|---|
| 8–9 | Strong |
| 5–7 | Moderate |
| 2–4 | Limited |
| 0–1 | Weak |

***

## Ethereum / PeerDAS

| Axis | # | Sub-property | Level | Evidence |
|---|---|---|:---:|---|
| Retrievability | R1 | Data redundancy | 2 | 1D Reed-Solomon, 2× extension (64→128 columns), with reconstruction from ≥50% of columns specified [ETH-10] |
| | R2 | Retrieval path independence | 2 | Two retrieval paths: from custody peers, and reconstruction from peers holding ≥64 columns [ethereum/README] |
| | R3 | Sampling vs full-download | 1 | "DAS" here is peer-to-peer column distribution; fork-choice gates on custody, not randomized sampling; 2D sampling deferred [ETH-11, ETH-10] |
| Verifiability | V1 | Independent verification | 2 | Each validator verifies its own custody sidecars and their KZG proofs; partial (custody subset), no separate peer-sampling gate [ETH-11] |
| | V2 | Bridge / settlement verification | N/A | Ethereum is the base layer; DA is verified by its own consensus, with no external settlement bridge. Not applicable — excluded from the Verifiability band [ethereum/README] |
| | V3 | Dishonesty deterrent | 0 | Column custody is self-reported in the ENR and not attributable, so withholding carries no enforceable penalty [ETH-07, ETH-11] |
| Liveness | L1 | Consensus / service continuity | 3 | Consensus needs >2/3 of ~1M validators; a robust BFT margin [ethereum/README] |
| | L2 | Write path resilience | 3 | Blob transactions enter through any L1 full node; column sidecars gossip over 128 per-column subnets; no single write controller [ethereum/README] |
| | L3 | Read path resilience | 3 | Distributed gossip over 128 per-column subnets, with no single read controller [ethereum/README] |
| Decentralization | D1 | Operator / validator distribution | 3 | Global validator set (~1M); custody is peer-driven with no operator cartel [ethereum/README] |
| | D2 | Governance concentration | 3 | Protocol change via the EIP process and multiple independent client teams; no multisig controls PeerDAS; KZG setup is one-time and immutable [ethereum/README] |
| | D3 | Software & infra diversity | 3 | Multiple independent clients (Lighthouse, Prysm, go-ethereum…); `c-kzg` is a shared dependency but cross-verified across clients [ethereum/README] |
| Cost Efficiency | C1 | Fee predictability | 3 | EIP-4844 excess-blob-gas gives a bounded, dynamic blob-fee market [ETH-12] |
| | C2 | Blockspace manipulation resistance | 3 | EIP-7918 sets a blob base-fee reserve that resists draining blob space cheaply [ETH-12] |
| | C3 | Throughput capacity | 2 | ~6 blobs/slot × 128 KB over ~12 s; moderate throughput [ethereum/README] |

**Axis bands** — Retrievability **Moderate** (5) · Verifiability **partial** (V1, V3 = 2, 0; V2 N/A) · Liveness **Strong** (9) · Decentralization **Strong** (9) · Cost Efficiency **Strong** (8).

***

## EigenDA

| Axis | # | Sub-property | Level | Evidence |
|---|---|---|:---:|---|
| Retrievability | R1 | Data redundancy | 2 | Reed-Solomon chunks across operators; reconstruction specified at the quorum/confirmation threshold, not independently production-demonstrated [eigenda/README] |
| | R2 | Retrieval path independence | 2 | Two paths: a relay layer and a direct `GetChunks` fallback to operators [eigenda/README] |
| | R3 | Sampling vs full-download | 0 | No data availability sampling; clients rely entirely on the quorum's BLS-aggregate attestation [EDA-12] |
| Verifiability | V1 | Independent verification | 1 | Quorum attestation only — on-chain certificate checks BLS signatures and the stake threshold; no client-side sampling or proof of custody [EDA-12] |
| | V2 | Bridge / settlement verification | 2 | Certificate verified on Ethereum (`EigenDACertVerificationLib`), but the trust assumption is the operator quorum, not a validity proof [EDA-12] |
| | V3 | Dishonesty deterrent | 0 | No slashing — the AVS operator-set count is 0 and no slashing events are observed; free-riding operators face no penalty [EDA-11, evidence.md: Slashing Absence] |
| Liveness | L1 | Consensus / service continuity | 2 | No consensus to halt, but a confirmation threshold; top-3 operators hold 39.80% (> the 33% safety margin), Nakamoto ≈ 3 [evidence.md: Operator Stake Distribution] |
| | L2 | Write path resilience | 1 | A centralized Disperser is the write path with no automatic failover; its reservation is governed by a 3-of-4 multisig [eigenda/README, EDA-07] |
| | L3 | Read path resilience | 2 | The read path provides a relay layer plus a direct `GetChunks` fallback to operators [eigenda/README] |
| Decentralization | D1 | Operator / validator distribution | 1 | 272 operators but top-3 hold 39.80% (> 33%), Nakamoto ≈ 3, HHI ≈ 883 [evidence.md: Operator Stake Distribution] |
| | D2 | Governance concentration | 1 | A single 3-of-4 multisig with no timelock owns 8 core contracts and the ProxyAdmin; arbitrary upgrade in one transaction [EDA-07] |
| | D3 | Software & infra diversity | 1 | Single node implementation; hosting concentrated — AWS 21.78%, top-5 providers ≈ 82.7% of Quorum-0 stake; Quorum-1 Herd ≈ 41.87% [evidence.md: Infrastructure Concentration] |
| Cost Efficiency | C1 | Fee predictability | 2 | Per-blob, quorum-based pricing with no congestion fee market; fees are relatively predictable but not a bounded market [eigenda/README] |
| | C2 | Blockspace manipulation resistance | — | Insufficient published evidence (no documented anti-monopoly mechanism) |
| | C3 | Throughput capacity | 2 | Bounded by operator bandwidth and Disperser capacity; no published throughput ceiling [eigenda/README] |

**Axis bands** — Retrievability **Limited** (4) · Verifiability **Limited** (3) · Liveness **Moderate** (5) · Decentralization **Limited** (3) · Cost Efficiency *partial* (C1, C3 = 2, 2; C2 unscored).

***

## Celestia

| Axis | # | Sub-property | Level | Evidence |
|---|---|---|:---:|---|
| Retrievability | R1 | Data redundancy | 3 | Reed-Solomon Extended Data Square; full-block reconstruction from ≥50% parity, live on mainnet [celestia/README] |
| | R2 | Retrieval path independence | 2 | DAS via shrex (primary) plus full-block download via bridge/validator full nodes; light nodes can fetch missing shares over the DHT [celestia/README] |
| | R3 | Sampling vs full-download | 3 | Light-client DAS in production — 16 random samples per node (`DefaultSampleAmount=16`) give statistical availability confidence [celestia/README] |
| Verifiability | V1 | Independent verification | 2 | Light nodes verify availability via DAS, but after BEFP removal there is no fraud proof for encoding correctness — availability only, not validity [CEL-11] |
| | V2 | Bridge / settlement verification | 2 | SP1Blobstream uses SP1 ZK proofs on Ethereum, but via a 4-of-6 multisig with zero timelock and all roles on one address [CEL-09, evidence.md: SP1Blobstream] |
| | V3 | Dishonesty deterrent | 1 | Downtime slashing exists but is effectively unparameterized (`slash_fraction_downtime=0`); no penalty for DA dishonesty, and prevote-nil censorship is undetectable [CEL-08, evidence.md: Validator Set & Slashing] |
| Liveness | L1 | Consensus / service continuity | 2 | CometBFT PoS, >2/3 finality, but top-8 validators hold 35.77% (> the 33% censorship margin); Nakamoto ≈ 8 [CEL-08] |
| | L2 | Write path resilience | 3 | Block production is spread across 94 active validators via CometBFT proposer election; no single point of write failure [celestia/README] |
| | L3 | Read path resilience | 3 | DAS distributes retrieval across the peer set, with full-node and DHT fallback; no single read controller [celestia/README] |
| Decentralization | D1 | Operator / validator distribution | 2 | 94 of 100 validators active; moderate set with concentration (top-8 = 35.77%, top-28 = 67.02%); Nakamoto ≈ 8 [CEL-08] |
| | D2 | Governance concentration | 1 | The SP1Blobstream bridge upgrade path is a 4-of-6 multisig with zero timelock (binding constraint), though chain protocol governance is broader [CEL-09] |
| | D3 | Software & infra diversity | 1 | A single primary implementation (celestia-core / celestia-node); validator hosting diversity not established [celestia/README] |
| Cost Efficiency | C1 | Fee predictability | 2 | Minimum gas price plus a dynamic fee market; an 8 MiB blob ≈ 0.134 TIA — generally low and bounded [evidence.md: Gas & Blockspace] |
| | C2 | Blockspace manipulation resistance | 1 | A low minimum gas price and a 32 MiB block make blockspace cheap to fill (≈ $0.25 per full block) [evidence.md: Gas & Blockspace] |
| | C3 | Throughput capacity | 2 | ≈ 32 MiB per 12 s block (≈ 2.67 MB/s) — moderate [evidence.md: Gas & Blockspace] |

**Axis bands** — Retrievability **Strong** (8) · Verifiability **Moderate** (5) · Liveness **Strong** (8) · Decentralization **Limited** (4) · Cost Efficiency **Moderate** (5).

***

## Avail

| Axis | # | Sub-property | Level | Evidence |
|---|---|---|:---:|---|
| Retrievability | R1 | Data redundancy | 2 | KZG-committed erasure coding with ≥50% reconstruction, but incomplete block reconstruction limits recovery [avail/README, AVL-12] |
| | R2 | Retrieval path independence | 2 | Light-client DAS (DHT/RPC fetch) plus full-node download; reconstruction completeness is a known limit [avail/README, AVL-12] |
| | R3 | Sampling vs full-download | 2 | Light clients perform DAS with a KZG verifier; coverage is partial given the reconstruction gap [avail/README, AVL-12] |
| Verifiability | V1 | Independent verification | 2 | Light clients verify sampled shares with KZG point-check proofs; client-side, partial [avail/README] |
| | V2 | Bridge / settlement verification | 2 | VectorX verifies SP1 ZK proofs on Ethereum, but the verifier is upgradeable and the deployer EOA retains admin [AVL-06] |
| | V3 | Dishonesty deterrent | 1 | NPoS slashing infrastructure exists (67 functions, 27-era deferral) but has never fired in 688 eras — not enforced [AVL-11, evidence.md: Avail Chain] |
| Liveness | L1 | Consensus / service continuity | 3 | NPoS (BABE + GRANDPA), 105 validators, Nakamoto ≈ 34, Phragmen keeps stake even (max/min ≈ 1.20×) [AVL-10, evidence.md: Avail Chain] |
| | L2 | Write path resilience | 3 | Decentralized BABE block production on the Avail chain; no single write controller [avail/README] |
| | L3 | Read path resilience | 3 | Avail-chain reads are distributed over DHT/RPC with full-node fallback; no single read controller [avail/README] |
| Decentralization | D1 | Operator / validator distribution | 3 | 105 active validators, Nakamoto ≈ 34, top validator ≈ 1.06% stake; Phragmen yields a very even distribution [AVL-10, evidence.md: Avail Chain] |
| | D2 | Governance concentration | 1 | AvailBridge is a 4-of-7 multisig with a 24 h timelock, but the VectorX deployer EOA retains `DEFAULT_ADMIN_ROLE`, enabling a 2-transaction solo upgrade that bypasses the multisig [AVL-06] |
| | D3 | Software & infra diversity | 1 | Single Substrate-based implementation [avail/README] |
| Cost Efficiency | C1 | Fee predictability | 2 | Substrate extrinsic fees scale with size and congestion; no DA-specific fee market [avail/README] |
| | C2 | Blockspace manipulation resistance | — | Insufficient published evidence (no documented anti-monopoly mechanism for Avail DA blockspace) |
| | C3 | Throughput capacity | 2 | Substrate 6 s BABE slots; throughput bounded by validator bandwidth and DHT capacity; no published blockspace ceiling [avail/README] |

**Axis bands** — Retrievability **Moderate** (6) · Verifiability **Moderate** (5) · Liveness **Strong** (9) · Decentralization **Moderate** (5) · Cost Efficiency *partial* (C1, C3 = 2, 2; C2 unscored).

***

## Cross-DA structural profile (bands)

| Axis | Ethereum | EigenDA | Celestia | Avail |
|---|---|---|---|---|
| Retrievability | Moderate (5) | Limited (4) | Strong (8) | Moderate (6) |
| Verifiability | partial | Limited (3) | Moderate (5) | Moderate (5) |
| Liveness | Strong (9) | Moderate (5) | Strong (8) | Strong (9) |
| Decentralization | Strong (9) | Limited (3) | Limited (4) | Moderate (5) |
| Cost Efficiency | Strong (8) | partial | Moderate (5) | partial |

> Bands describe **structural design only**, at the assessment's pinned versions. They do **not** reflect open vulnerabilities (see [Vulnerability burden](vulnerability-burden.md)) or live operational health (dashboard). A layer can hold a Strong structural band on an axis while carrying open vulnerabilities that currently pressure it — the two are reported separately on purpose. Ethereum's Verifiability is partial because V2 (external bridge verification) does not apply to a base layer.

***

## Reproducibility and how to contest a level

- Every level cites a primary source. To check a level, open the cited threat page or `evidence.md` section and compare the fact against the 0–3 anchor for that sub-property in [5-Axis Risk Scoring](../methodology/scoring.md).
- A level is **contestable**: if the cited evidence does not support the assigned integer under the anchor, the level should change. Disagreement is resolved against evidence, not opinion.
- `—` cells mark where published material is insufficient; they are excluded from the band rather than guessed. Closing those gaps (e.g., documenting blockspace-manipulation resistance for EigenDA and Avail) is tracked as future work.
- These levels are assigned as of the assessment date and the pinned commits/contract states recorded in each cited source. Re-assessment follows version changes.
