# EigenDA Monitoring System

BONDA operates a live monitoring system for EigenDA mainnet, providing real-time visibility into the protocol's operational health and threat indicators.

**Dashboard**: [bonda.me](https://bonda.me)
**Source**: [github.com/jyo-o/BONDA/eigenda](https://github.com/jyo-o/BONDA/eigenda)

## Architecture

The monitoring backend runs a 7-worker pipeline that continuously collects, verifies, and indexes EigenDA mainnet data.

| Worker | Function | Data Source |
|---|---|---|
| **BlobCollector** | Ingests new blobs from the disperser, tracks blob lifecycle (Encoded, Certified, Failed) | Disperser gRPC API |
| **RelayVerifier** | Monitors relay availability and retrieval success rates | Relay gRPC (relay-0-mainnet-ethereum.eigenda.xyz) |
| **OperatorVerifier** | Probes individual operator nodes for chunk serving health (GetChunks) | Operator gRPC endpoints |
| **Reverifier** | Re-verifies previously collected data for consistency checks | Internal data store |
| **WriteProber** | Active write probes to measure dispersal latency and success rates | Disperser gRPC API |
| **StakeIndexer** | Indexes on-chain stake distribution across quorums (Q0/Q1/Q2) | Ethereum mainnet (StakeRegistry) |
| **EjectionIndexer** | Tracks operator ejection events and ejector activity | Ethereum mainnet (EjectionManager) |

## Live Signals

The dashboard surfaces the following real-time metrics derived from the threat model:

### Signing Stake Percentage
The fraction of total quorum stake that signed each blob's attestation. Relates to **EDA-E03** (operator stake concentration) -- if signing stake drops below the confirmation threshold (55%), blob certification fails.

### Nakamoto Coefficient
The minimum number of operators needed to control 33% of stake in each quorum. Directly measures the **EDA-E03** collusion threshold. Current mainnet values: Q0 Nakamoto=3, Q1 Nakamoto=3.

### Dead Operators
Operators with 0% chunk serving success rate over the monitoring window. Relates to **EDA-D12** (dead operators) and **EDA-P01** (no slashing incentive). Mainnet observation: 11 out of 79 probed operators at 0% success rate. These are free-rider candidates -- they sign BLS attestations but do not serve data.

### Relay Health
Availability status of the single registered relay (EDA-D06). Since only 1 relay is registered on-chain (RelayRegistry nextRelayKey=1), any downtime directly affects the primary blob retrieval path.

### Ejection Activity
Historical and real-time ejection events from the EjectionManager contract. Relates to **EDA-T09** (ejector role abuse). The ejector is a single EOA (0x8642...) that can remove up to 33.33% of quorum stake within a 3-day window.

## Threat Coverage

The monitoring system provides observability for the following threat findings:

| Threat ID | Signal | Coverage |
|---|---|---|
| EDA-D06 | Relay uptime, retrieval latency | Direct monitoring |
| EDA-D12 | Per-operator chunk serving success rate | Direct monitoring |
| EDA-E03 | Stake distribution, Nakamoto coefficient, HHI | On-chain indexing |
| EDA-T09 | Ejection event count, ejector address activity | On-chain indexing |
| EDA-P01 | Slash event count (expected: 0) | On-chain indexing |
| EDA-D03 | Disperser response times, error rates | Write probe data |
| G-CON-03 | Operator IP/ASN diversity metrics | Operator probe metadata |
