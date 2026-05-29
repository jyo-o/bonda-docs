# Table of contents

* [Overview](README.md)

## Methodology

* [Overview](methodology/README.md)
* [STRIDE for DA Layers](methodology/stride.md)
* [BVSS 1.1 Scoring](methodology/bvss.md)
* [Verification Approach](methodology/verification.md)

## EigenDA

* [Overview](eigenda/README.md)
* [EDA-D02: Proxy Rate Limit Absence](eigenda/threats/eda-d02.md)
* [EDA-S03: Cross-chain Signature Replay](eigenda/threats/eda-s03.md)
* [EDA-D03: Disperser V2 KZG Unauthenticated Exposure](eigenda/threats/eda-d03.md)
* [EDA-E01: Anchor Signature Verification Bypass](eigenda/threats/eda-e01.md)
* [EDA-D04: Blob Encoding Failure No Fallback](eigenda/threats/eda-d04.md)
* [EDA-I02: BLS Private Key Exposure](eigenda/threats/eda-i02.md)
* [EDA-D06: Relay Single Point of Failure](eigenda/threats/eda-d06.md)
* [EDA-D07: GetBlob No Authentication](eigenda/threats/eda-d07.md)
* [EDA-E02: Single 3-of-4 Multisig Controls 8 Core Contracts](eigenda/threats/eda-e02.md)
* [EDA-T09: Ejector Role Abuse](eigenda/threats/eda-t09.md)
* [EDA-T10: PutAttestation Unconditional Overwrite](eigenda/threats/eda-t10.md)
* [EDA-D10: Unauthenticated POST Flood on Proxy](eigenda/threats/eda-d10.md)
* [EDA-D12: Dead Operators — 0% Chunk Serving](eigenda/threats/eda-d12.md)
* [EDA-E03: Operator Stake Concentration](eigenda/threats/eda-e03.md)
* [G-CON-03: Operator Infrastructure Concentration](eigenda/threats/g-con-03.md)
* [EDA-P01: Operator Slashing Not Implemented](eigenda/threats/eda-p01.md)
* [EDA-P02: No DAS — Full Quorum Trust Required](eigenda/threats/eda-p02.md)
* [Monitoring](eigenda/monitoring.md)

## Celestia

* [Overview](celestia/README.md)
* [CEL-D01: Zero-cost Prevote-nil Censorship](celestia/threats/cel-d01.md)
* [CEL-D02: Large PFB Blockspace Monopoly](celestia/threats/cel-d02.md)
* [CEL-D04: Evidence Subsystem Code Flaws](celestia/threats/cel-d04.md)
* [CEL-D05: ShrEx Response Size Unlimited](celestia/threats/cel-d05.md)
* [CEL-T01: DAS-only Safety Model Misrepresentation](celestia/threats/cel-t01.md)
* [CEL-E01: SP1Blobstream Instant Upgrade via Multisig](celestia/threats/cel-e01.md)
* [CEL-S01: DAS Selective Disclosure via Sybil Peers](celestia/threats/cel-s01.md)
* [G-CON-01: KYC Validator Concentration — Legal Censorship](celestia/threats/g-con-01.md)
* [G-OPS-01: Multi-surface Information Asymmetry](celestia/threats/g-ops-01.md)
* [CEL-D10: NamespaceData Worst-case Memory Reservation](celestia/threats/cel-d10.md)
* [CEL-D12: GetProposal Nil Pointer Panic](celestia/threats/cel-d12.md)
* [CEL-D13: CheckTx Gas Metering Bypass](celestia/threats/cel-d13.md)
* [CEL-D14: ProcessProposal TxCache Bypass](celestia/threats/cel-d14.md)
* [CEL-D15: blob.Subscribe Infinite Retry CPU Burn](celestia/threats/cel-d15.md)
* [CEL-D17: TxCache Key Mismatch — Validator OOM](celestia/threats/cel-d17.md)
* [CEL-D03: blacklistedHashes Unbounded Memory Growth](celestia/threats/cel-d03.md)
* [CEL-D06: EnableBlackListing Default Disabled](celestia/threats/cel-d06.md)
* [Attack Chains](celestia/attack-chains.md)

## Avail

* [Overview](avail/README.md)
* [AVL-D01: VectorX Single Relayer SPOF](avail/threats/avl-d01.md)
* [AVL-E03: Deployer EOA Admin Role Retention](avail/threats/avl-e03.md)
* [AVL-T01: VectorX Instant Upgrade — No Timelock](avail/threats/avl-t01.md)
* [AVL-E04: Technical Committee Runtime Upgrade](avail/threats/avl-e04.md)
* [AVL-T05: KZG Trusted Setup Assumption](avail/threats/avl-t05.md)
* [AVL-E01: SP1VerifierGateway 2/3 Multisig](avail/threats/avl-e01.md)
* [AVL-T03: AVAIL Token Infinite Mint via Bridge](avail/threats/avl-t03.md)
* [AVL-T04: Guardian ZK Proof Bypass](avail/threats/avl-t04.md)
* [AVL-D02: Validator Set Underutilization](avail/threats/avl-d02.md)
* [AVL-I01: Block Reconstruction Incomplete](avail/threats/avl-i01.md)
* [AVL-E02: Multisig Key Holder Triple Overlap](avail/threats/avl-e02.md)
* [AVL-R01: Slashing Infrastructure Dormant](avail/threats/avl-r01.md)
* [AVL-T02: Bridge 24h Timelock — Limited Risk](avail/threats/avl-t02.md)
* [AVL-S01: TimelockedUpgradeable Name Deception](avail/threats/avl-s01.md)
* [PoC Evidence](avail/poc-evidence.md)

## Ethereum / PeerDAS

* [Overview](ethereum/README.md)
* [ETH-S01: Testing API JWT Authentication Missing](ethereum/threats/eth-s01.md)
* [ETH-S02: Custody Group Node ID Grinding](ethereum/threats/eth-s02.md)
* [ETH-T01: Blob Fee Denominator Fork Dependency](ethereum/threats/eth-t01.md)
* [ETH-T02: KZG Trusted Setup File Replacement](ethereum/threats/eth-t02.md)
* [ETH-T03: Data Column Inclusion Proof Omission](ethereum/threats/eth-t03.md)
* [ETH-T04: Cell Index Bounds Check Asymmetry](ethereum/threats/eth-t04.md)
* [ETH-T05: Column Proof Verification Gap](ethereum/threats/eth-t05.md)
* [ETH-R01: Blob/DataColumn Equivocation Detection Failure](ethereum/threats/eth-r01.md)
* [ETH-D01: Per-Account Blobpool Exhaustion](ethereum/threats/eth-d01.md)
* [ETH-D02: Verified Column Discard on Reconstruction Failure](ethereum/threats/eth-d02.md)
* [ETH-E01: Reconstruction Failure Mode Mismatch](ethereum/threats/eth-e01.md)

## Cross-DA Comparison

* [Overview](comparison/README.md)
* [Scoring Comparison](comparison/scoring.md)
* [Common Patterns](comparison/common-patterns.md)
