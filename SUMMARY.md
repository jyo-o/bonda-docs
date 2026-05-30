# Table of contents

* [Overview](README.md)

## Methodology

* [Overview](methodology/README.md)
* [STRIDE for DA Layers](methodology/stride.md)
* [CVSS 3.1 Scoring](methodology/cvss.md)
* [Verification Approach](methodology/verification.md)
* [Terminology](methodology/terminology.md)

## EigenDA

* [Overview](eigenda/README.md)
* [EDA-T09: Ejector Role Abuse](eigenda/threats/eda-t09.md)
* [EDA-D06: Relay Single Point of Failure](eigenda/threats/eda-d06.md)
* [EDA-E03: Operator Stake Concentration](eigenda/threats/eda-e03.md)
* [EDA-P01: Slashing Not Implemented](eigenda/threats/eda-p01.md)
* [EDA-P02: No DAS](eigenda/threats/eda-p02.md)
* [EDA-D03: Disperser V2 KZG Unauthenticated](eigenda/threats/eda-d03.md)
* [EDA-G01: Infrastructure Concentration](eigenda/threats/eda-g01.md)
* [EDA-S03: Signature Replay](eigenda/threats/eda-s03.md)
* [EDA-I02: BLS Key Exposure](eigenda/threats/eda-i02.md)
* [EDA-E02: Single Multisig Controls 8 Contracts](eigenda/threats/eda-e02.md)
* [EDA-D12: Dead Operators](eigenda/threats/eda-d12.md)
* [EDA-D07: GetBlob No Authentication](eigenda/threats/eda-d07.md)
* [EDA-E01: Anchor Verification Bypass](eigenda/threats/eda-e01.md)
* [EDA-T10: Attestation Overwrite](eigenda/threats/eda-t10.md)
* [EDA-D02: Proxy Rate Limit Absence](eigenda/threats/eda-d02.md)
* [EDA-D10: Unauthenticated POST Flood](eigenda/threats/eda-d10.md)
* [EDA-D04: Encoding Failure No Fallback](eigenda/threats/eda-d04.md)
* [Monitoring](eigenda/monitoring.md)

## Celestia

* [Overview](celestia/README.md)
* [CEL-E01: SP1Blobstream Instant Upgrade](celestia/threats/cel-e01.md)
* [CEL-G01: KYC Validator Censorship](celestia/threats/cel-g01.md)
* [CEL-T01: DAS-only Safety Model](celestia/threats/cel-t01.md)
* [CEL-G02: Information Asymmetry](celestia/threats/cel-g02.md)
* [CEL-D11: pendingSeenTracker Memory Growth](celestia/threats/cel-d11.md)
* [CEL-D13: CheckTx Pre-gas Commitment](celestia/threats/cel-d13.md)
* [CEL-D17: TxCache Key Mismatch OOM](celestia/threats/cel-d17.md)
* [CEL-D02: Blockspace Monopoly](celestia/threats/cel-d02.md)
* [CEL-D03: blacklistedHashes Memory Growth](celestia/threats/cel-d03.md)
* [CEL-D06: Peer Blacklisting Disabled](celestia/threats/cel-d06.md)
* [CEL-D12: GetProposal Nil Pointer Panic](celestia/threats/cel-d12.md)
* [CEL-D15: blob.Subscribe Infinite Retry](celestia/threats/cel-d15.md)
* [CEL-D04: Evidence Subsystem Defects](celestia/threats/cel-d04.md)
* [CEL-D10: Namespace Memory Reservation](celestia/threats/cel-d10.md)
* [CEL-D14: ProcessProposal TxCache Bypass](celestia/threats/cel-d14.md)
* [CEL-S01: DAS Selective Disclosure](celestia/threats/cel-s01.md)
* [CEL-D01: Prevote-nil Censorship](celestia/threats/cel-d01.md)
* [CEL-D05: ShrEx Unbounded Response](celestia/threats/cel-d05.md)
* [Attack Chains](celestia/attack-chains.md)

## Avail

* [Overview](avail/README.md)
* [AVL-E03: Deployer Retains Admin Role](avail/threats/avl-e03.md)
* [AVL-D01: Single Relayer SPOF](avail/threats/avl-d01.md)
* [AVL-D02: Low Validator Utilization](avail/threats/avl-d02.md)
* [AVL-T05: KZG Trusted Setup](avail/threats/avl-t05.md)
* [AVL-E04: Technical Committee Upgrade](avail/threats/avl-e04.md)
* [AVL-T01: VectorX Instant Upgrade](avail/threats/avl-t01.md)
* [AVL-E01: SP1 Verifier Multisig](avail/threats/avl-e01.md)
* [AVL-T03: Unlimited Token Minting](avail/threats/avl-t03.md)
* [AVL-T04: Guardian ZK Proof Bypass](avail/threats/avl-t04.md)
* [AVL-I01: Incomplete Block Reconstruction](avail/threats/avl-i01.md)
* [AVL-E02: Multisig Key Overlap](avail/threats/avl-e02.md)
* [AVL-R01: Slashing Never Triggered](avail/threats/avl-r01.md)
* [AVL-T02: Bridge 24h Timelock](avail/threats/avl-t02.md)
* [AVL-S01: Misleading Contract Name](avail/threats/avl-s01.md)
* [PoC Evidence](avail/poc-evidence.md)

## Ethereum / PeerDAS

* [Overview](ethereum/README.md)
* [ETH-S01: Testing API JWT Bypass](ethereum/threats/eth-s01.md)
* [ETH-S02: Custody Group Node ID Grinding](ethereum/threats/eth-s02.md)
* [ETH-T01: Blob Fee Fork Dependency](ethereum/threats/eth-t01.md)
* [ETH-T02: KZG Trusted Setup File Replacement](ethereum/threats/eth-t02.md)
* [ETH-T03: Data Column Inclusion Proof Omission](ethereum/threats/eth-t03.md)
* [ETH-T04: Cell Index Bounds Check Asymmetry](ethereum/threats/eth-t04.md)
* [ETH-T05: Column Proof Verification Gap](ethereum/threats/eth-t05.md)
* [ETH-R01: Equivocation Detection Failure](ethereum/threats/eth-r01.md)
* [ETH-D01: Per-Account Blobpool Exhaustion](ethereum/threats/eth-d01.md)
* [ETH-D02: Verified Column Discard](ethereum/threats/eth-d02.md)
* [ETH-E01: Reconstruction Failure Mode Mismatch](ethereum/threats/eth-e01.md)

## Cross-DA Comparison

* [Overview](comparison/README.md)
* [Scoring Comparison](comparison/scoring.md)
* [Common Patterns](comparison/common-patterns.md)
