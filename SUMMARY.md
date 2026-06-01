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
* [EDA-E02: Single Multisig Controls 8 Contracts](eigenda/threats/eda-e02.md)
* [EDA-D12: Dead Operators](eigenda/threats/eda-d12.md)
* [EDA-D07: GetBlob No Authentication](eigenda/threats/eda-d07.md)
* [EDA-E01: Anchor Verification Bypass](eigenda/threats/eda-e01.md)
* [EDA-D02: Proxy Rate Limit Absence](eigenda/threats/eda-d02.md)
* [Verification Evidence](eigenda/evidence.md)
* [Monitoring](eigenda/monitoring.md)

## Celestia

* [Overview](celestia/README.md)
* [CEL-E01: SP1Blobstream Instant Upgrade](celestia/threats/cel-e01.md)
* [CEL-G01: KYC Validator Censorship](celestia/threats/cel-g01.md)
* [CEL-P01: DAS-only Safety Model](celestia/threats/cel-p01.md)
* [CEL-G02: Information Asymmetry](celestia/threats/cel-g02.md)
* [CEL-D13: CheckTx Pre-gas Commitment](celestia/threats/cel-d13.md)
* [CEL-D17: TxCache Key Mismatch OOM](celestia/threats/cel-d17.md)
* [CEL-D02: Blockspace Monopoly](celestia/threats/cel-d02.md)
* [CEL-D03: blacklistedHashes Memory Growth](celestia/threats/cel-d03.md)
* [CEL-D06: Peer Blacklisting Disabled](celestia/threats/cel-d06.md)
* [CEL-D15: blob.Subscribe Infinite Retry](celestia/threats/cel-d15.md)
* [CEL-D05: ShrEx Unbounded Response Size](celestia/threats/cel-d05.md)
* [CEL-S01: DAS Selective Disclosure](celestia/threats/cel-s01.md)
* [Attack Chains](celestia/attack-chains.md)
* [Verification Evidence](celestia/evidence.md)

## Avail

* [Overview](avail/README.md)
* [AVL-E03: Deployer Retains Admin Role](avail/threats/avl-e03.md)
* [AVL-D01: Single Relayer SPOF](avail/threats/avl-d01.md)
* [AVL-D02: Low Validator Utilization](avail/threats/avl-d02.md)
* [AVL-T01: VectorX Instant Upgrade](avail/threats/avl-t01.md)
* [AVL-E01: SP1 Verifier Multisig](avail/threats/avl-e01.md)
* [AVL-T03: Unlimited Token Minting](avail/threats/avl-t03.md)
* [AVL-P02: Incomplete Block Reconstruction](avail/threats/avl-p02.md)
* [AVL-E02: Multisig Key Overlap](avail/threats/avl-e02.md)
* [AVL-P01: Slashing Never Triggered](avail/threats/avl-p01.md)
* [Verification Evidence](avail/evidence.md)

## Ethereum / PeerDAS

* [Overview](ethereum/README.md)
* [ETH-T01: Missing Subgroup Check](ethereum/threats/eth-r01.md)
* [ETH-D02: Rate Limit Bypass](ethereum/threats/eth-r02.md)
* [ETH-D03: Incorrect Timeout](ethereum/threats/eth-r03.md)
* [ETH-T04: Go Binding Thread Safety](ethereum/threats/eth-r04.md)

## Cross-DA Comparison

* [Overview](comparison/README.md)
* [Scoring Comparison](comparison/scoring.md)
* [Common Patterns](comparison/common-patterns.md)
