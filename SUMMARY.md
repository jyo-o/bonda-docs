# Table of contents

* [Overview](README.md)

## Methodology

* [Overview](methodology/README.md)
* [Threat Classification](methodology/classification.md)
* [Severity & Scoring](methodology/scoring.md)
* [CVSS 3.1 Scoring](methodology/cvss.md)
* [Verification Approach](methodology/verification.md)
* [Terminology](methodology/terminology.md)

## Ethereum

* [Overview](ethereum/README.md)
* [ETH-01: DataColumnsByRange Rate-Limit Bypass](ethereum/threats/eth-01.md)
* [ETH-02: c-kzg Missing Subgroup Check](ethereum/threats/eth-02.md)
* [ETH-03: DataColumnsByRoot Incorrect Timeout](ethereum/threats/eth-03.md)
* [ETH-04: c-kzg Go Binding Thread Safety](ethereum/threats/eth-04.md)
* [ETH-05: Reconstruction Depends on Half-Column Holders](ethereum/threats/eth-05.md)
* [ETH-06: Per-Column Subnet Eclipse](ethereum/threats/eth-06.md)
* [ETH-07: Self-Reported Custody Count Unverifiable](ethereum/threats/eth-07.md)
* [ETH-08: Builder/Relay Publication Concentration](ethereum/threats/eth-08.md)
* [ETH-09: Rising Node Resource Floor](ethereum/threats/eth-09.md)
* [ETH-10: One-Dimensional Erasure Coding](ethereum/threats/eth-10.md)
* [ETH-11: Fork-Choice Rests on Custody](ethereum/threats/eth-11.md)
* [ETH-12: EIP-7918 Blob Fee Reserve](ethereum/threats/eth-12.md)

## EigenDA

* [Overview](eigenda/README.md)
* [EDA-01: GetChunks Cold-Miss CPU Exhaustion](eigenda/threats/eda-01.md)
* [EDA-02: Disperser V2 KZG Compute Surface](eigenda/threats/eda-02.md)
* [EDA-03: Cross-Chain Signature Replay](eigenda/threats/eda-03.md)
* [EDA-04: Relay Single Point of Failure](eigenda/threats/eda-04.md)
* [EDA-05: GetBlob Global-Only Rate Limiting](eigenda/threats/eda-05.md)
* [EDA-06: Dead Operators Serving Zero Chunks](eigenda/threats/eda-06.md)
* [EDA-07: Single Multisig Controls Core Contracts](eigenda/threats/eda-07.md)
* [EDA-08: Ejector Role Abuse](eigenda/threats/eda-08.md)
* [EDA-09: Operator Stake Concentration](eigenda/threats/eda-09.md)
* [EDA-10: Anchor Verification Disable Flag](eigenda/threats/eda-10.md)
* [EDA-11: Slashing Not Implemented](eigenda/threats/eda-11.md)
* [EDA-12: No Data Availability Sampling](eigenda/threats/eda-12.md)
* [EDA-13: Proxy Missing Rate Limiting](eigenda/threats/eda-13.md)
* [EDA-14: Infrastructure Concentration](eigenda/threats/eda-14.md)
* [Attack Chains](eigenda/attack-chains.md)
* [Verification Evidence](eigenda/evidence.md)
* [Monitoring](eigenda/monitoring.md)

## Celestia

* [Overview](celestia/README.md)
* [CEL-01: TxCache Key Mismatch OOM](celestia/threats/cel-01.md)
* [CEL-02: blob.Subscribe Infinite Retry](celestia/threats/cel-02.md)
* [CEL-03: blacklistedHashes Memory Growth](celestia/threats/cel-03.md)
* [CEL-04: CheckTx Pre-gas Commitment](celestia/threats/cel-04.md)
* [CEL-05: Blockspace Monopoly](celestia/threats/cel-05.md)
* [CEL-06: Peer Blacklisting Disabled](celestia/threats/cel-06.md)
* [CEL-07: DAS Selective Disclosure](celestia/threats/cel-07.md)
* [CEL-08: KYC Validator Concentration](celestia/threats/cel-08.md)
* [CEL-09: SP1Blobstream Instant Upgrade](celestia/threats/cel-09.md)
* [CEL-10: Documentation Drift](celestia/threats/cel-10.md)
* [CEL-11: DAS-Only Safety Model](celestia/threats/cel-11.md)
* [CEL-12: ShrEx Unbounded Response Size](celestia/threats/cel-12.md)
* [Attack Chains](celestia/attack-chains.md)
* [Verification Evidence](celestia/evidence.md)

## Avail

* [Overview](avail/README.md)
* [AVL-01: MultiAddress::Index Bridge Proof Omission](avail/threats/avl-01.md)
* [AVL-02: Proxy-Wrapped submitData DA Bypass](avail/threats/avl-02.md)
* [AVL-03: Kate RPC Unauthenticated KZG DoS](avail/threats/avl-03.md)
* [AVL-04: Single Relayer Bridge SPOF](avail/threats/avl-04.md)
* [AVL-05: VectorX Instant Upgrade](avail/threats/avl-05.md)
* [AVL-06: Deployer EOA Retains Admin Role](avail/threats/avl-06.md)
* [AVL-07: SP1VerifierGateway Multisig](avail/threats/avl-07.md)
* [AVL-08: Multisig Key Overlap](avail/threats/avl-08.md)
* [AVL-09: Unlimited Token Minting via Upgrade](avail/threats/avl-09.md)
* [AVL-10: Low Validator Utilization](avail/threats/avl-10.md)
* [AVL-11: Slashing Never Triggered](avail/threats/avl-11.md)
* [AVL-12: Incomplete Block Reconstruction](avail/threats/avl-12.md)
* [Attack Chains](avail/attack-chains.md)
* [Verification Evidence](avail/evidence.md)

## Cross-DA Comparison

* [Overview](comparison/README.md)
* [Scoring Comparison](comparison/scoring.md)
* [Structural Baselines](comparison/baselines.md)
* [Vulnerability Burden](comparison/vulnerability-burden.md)
* [Common Patterns](comparison/common-patterns.md)
