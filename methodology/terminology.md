# Terminology

This glossary provides definitions for the key terms used throughout the BONDA threat model. It is intended as a quick reference for readers who may be unfamiliar with blockchain security, data availability infrastructure, or the specific frameworks and tools referenced in our analysis.

Terms are grouped by category. For deeper context, follow the cross-references to other methodology pages.

---

## General Blockchain & Data Availability

| Term | Definition |
|------|------------|
| **Data Availability (DA)** | The guarantee that transaction data published to a blockchain is retrievable by any participant for a defined period. Rollups depend on DA layers to ensure their state can always be independently reconstructed. |
| **Data Availability Sampling (DAS)** | A technique that allows light nodes to verify data availability without downloading the entire dataset. Nodes sample random chunks and use erasure coding properties to gain statistical confidence that the full data is available. |
| **Blob** | A binary large object attached to a transaction, used to carry rollup data on DA layers. On Ethereum, blob transactions were introduced in EIP-4844 and are priced separately from calldata. |
| **KZG Commitment** | A polynomial commitment scheme that allows a prover to commit to a polynomial and later prove evaluations at specific points. DA layers use KZG commitments to enable efficient verification that blobs are correctly encoded without downloading them in full. |
| **Erasure Coding** | A data encoding technique that expands original data with redundant fragments so that the full dataset can be reconstructed from any sufficiently large subset. DA layers use erasure coding to ensure data can survive partial loss or withholding. |
| **Reed-Solomon Encoding** | The specific erasure coding algorithm used by most DA layers, including EigenDA and Ethereum PeerDAS. It encodes data as polynomial evaluations, enabling reconstruction from any k-of-n encoded chunks. |
| **Namespace** | A logical partition of blob data within a DA layer. Celestia and Avail use namespaces to let rollups retrieve only the data relevant to them rather than downloading the entire block. |
| **Light Node** | A node that verifies blockchain data using block headers and proofs rather than downloading and re-executing all transactions. In DA contexts, light nodes perform DAS to confirm data availability. |
| **Full Node** | A node that downloads, stores, and validates all blockchain data. Full nodes provide the highest security guarantee but require significantly more resources than light nodes. |
| **Trusted Setup** | A one-time cryptographic ceremony that generates structured reference parameters required by KZG commitments. Also called Powers of Tau. If the setup is compromised, a malicious actor could forge valid-looking proofs. The security assumption is that at least one participant in the ceremony was honest. |

---

## Security & Threat Modeling

| Term | Definition |
|------|------------|
| **STRIDE** | A threat classification framework developed by Microsoft. Each letter represents a category of threat. See the [STRIDE for DA Layers](stride.md) page for how BONDA extends this framework with DA-specific categories. |
| **Spoofing** | Pretending to be another entity. In DA contexts: forging operator identities, replaying cross-chain signatures, or impersonating disperser nodes. |
| **Tampering** | Unauthorized modification of data or state. Examples include overwriting attestation records, altering blob encodings, or manipulating validator sets. |
| **Repudiation** | The ability to deny having performed an action. In DA systems, weak logging or missing equivocation detection can allow nodes to deny misbehavior. |
| **Information Disclosure** | Exposure of data to unauthorized parties. Examples include BLS private key leakage, unprotected gRPC endpoints, or unauthenticated API access revealing internal state. |
| **Denial of Service** | Disrupting the availability of a system or service. DA-specific examples include blob flooding, mempool exhaustion, unbounded memory growth, and operator liveness failures. |
| **Elevation of Privilege** | Gaining access or control beyond what is authorized. In DA layers, this includes multisig abuse, proxy upgrade hijacking, and role escalation through governance mechanisms. |
| **CVSS** | Common Vulnerability Scoring System (version 3.1). The industry-standard severity scoring framework used by NVD, major audit firms, and bug bounty platforms. See [CVSS 3.1 Scoring](cvss.md). |
| **DFD** | Data Flow Diagram. A visual representation of how data moves between components, processes, and data stores. DFDs are annotated with trust boundaries to identify where security transitions occur. |
| **Trust Boundary** | A line in a DFD where data crosses between entities with different privilege levels. Threats are most likely to occur at trust boundaries, making them the primary focus of STRIDE analysis. |
| **Attack Surface** | The sum of all points where an unauthorized actor can attempt to interact with a system. A larger attack surface generally means more potential entry points for exploitation. |
| **Attack Chain** | A sequence of individually low-severity vulnerabilities that, when combined, produce a high-severity outcome. BONDA documents attack chains to show how threats can compound across trust boundaries. |
| **Single Point of Failure (SPOF)** | A component whose failure causes the entire system or a critical subsystem to stop functioning. DA examples include sole-relayer bridges and single-disperser architectures. |
| **Nakamoto Coefficient** | The minimum number of independent entities that must collude to disrupt a decentralized network. A higher coefficient indicates greater decentralization and resilience against coordinated attacks. |

---

## On-Chain Governance

| Term | Definition |
|------|------------|
| **Multisig** | A smart contract wallet that requires multiple private key holders to approve a transaction before it executes. Gnosis Safe is the most common implementation. BONDA tracks multisig composition to identify governance concentration risks. |
| **Timelock** | A smart contract mechanism that enforces a mandatory delay between when an action is proposed and when it can be executed. Timelocks give the community time to review and react to governance actions such as contract upgrades. |
| **EOA** | Externally Owned Account. A blockchain account controlled by a single private key with no on-chain logic. EOAs holding admin roles represent a higher risk than multisigs because a single key compromise grants full control. |
| **UUPS Proxy** | Universal Upgradeable Proxy Standard. An upgrade pattern where the upgrade logic resides in the implementation contract rather than the proxy. The implementation can authorize its own replacement, making the upgrade authority a critical security parameter. |
| **Transparent Proxy** | An upgrade pattern where the proxy contract itself contains the upgrade logic, and only a designated admin address can trigger upgrades. All other callers are transparently forwarded to the implementation. |
| **Role-Based Access Control (RBAC)** | A permission model where smart contract functions are restricted to specific roles such as owner, pauser, or upgrader. BONDA examines RBAC configurations to assess whether role assignments create concentration risks. |
| **Slashing** | A penalty mechanism that destroys a portion of a validator's or operator's staked tokens in response to provable misbehavior. The absence of slashing is a recurring finding across DA layers, as it removes the economic deterrent against malicious behavior. |

---

## Protocol-Specific

| Term | Definition |
|------|------------|
| **AVS** | Actively Validated Service. In EigenLayer's restaking framework, an AVS is a service that leverages restaked ETH for its security. EigenDA operates as an AVS, meaning its operators are EigenLayer restakers who opt in to validate data availability. |
| **Disperser** | The EigenDA component responsible for encoding blobs, generating KZG commitments, and distributing data chunks to operators. Currently operated as a centralized service by EigenLabs. |
| **Relay** | An EigenDA component that caches and serves blob data to retrievers. Relays sit between operators and consumers, and their availability directly affects data retrieval latency. |
| **Operator** | In EigenDA, a node operator who has opted into the AVS to store and serve data chunks. Operators receive delegated restaked ETH and are expected to maintain high uptime, though slashing for failures is not yet implemented. |
| **CometBFT** | The Byzantine Fault Tolerant consensus engine used by Celestia, derived from Tendermint. It provides instant finality once two-thirds of validators sign a block. |
| **GRANDPA** | GHOST-based Recursive ANcestor Deriving Prefix Agreement. The finality gadget used by Avail's Substrate-based chain. GRANDPA finalizes chains of blocks rather than individual blocks, providing deterministic finality. |
| **BABE** | Blind Assignment for Blockchain Extension. The block production mechanism used alongside GRANDPA in Avail. BABE assigns block production slots to validators using a VRF-based lottery. |
| **VectorX** | Avail's ZK-based bridge contract that verifies Avail consensus proofs on Ethereum. VectorX uses SP1 proofs to validate GRANDPA and BABE state transitions without re-executing them on-chain. |
| **SP1Blobstream** | Celestia's bridge contract that relays Celestia block commitments to Ethereum using SP1 zero-knowledge proofs. It enables Ethereum smart contracts to verify that data was made available on Celestia. |
| **SP1** | Succinct Processor 1. A general-purpose ZK virtual machine developed by Succinct Labs. Both VectorX and SP1Blobstream use SP1 to generate zero-knowledge proofs of consensus and data availability. |
| **PeerDAS** | Peer Data Availability Sampling. Ethereum's planned extension of EIP-4844 that distributes data columns across the peer-to-peer network and enables nodes to verify data availability through sampling rather than full download. |
| **Custody Group** | In Ethereum's PeerDAS design, a set of data columns that a node is responsible for storing and serving. Custody group assignments are derived from a node's peer ID, making them a potential target for grinding attacks. |

---

## Verification Terms

| Term | Definition |
|------|------------|
| **verified** | Full verification. The threat's exploitability has been confirmed against production infrastructure through mainnet probes or live system testing. See [Verification Approach](verification.md). |
| **code_verified** | The vulnerable code path has been traced through source code at a pinned commit. Parameters and control flow are confirmed, but no live exploitation was performed. See [Verification Approach](verification.md). |
| **poc_verified** | A Proof of Concept demonstrates the mechanism in a controlled environment, confirming the threat is reproducible under test conditions. See [Verification Approach](verification.md). |
| **partial** | Some evidence supports the finding, but defense boundaries or environmental factors prevent full confirmation. Acknowledged limitations are documented. See [Verification Approach](verification.md). |
| **unverified** | The threat is identified through design analysis or documentation review but lacks primary-source confirmation. See [Verification Approach](verification.md). |
| **PoC** | Proof of Concept. A minimal, reproducible demonstration that a vulnerability can be triggered. BONDA PoCs are typically shell scripts using Foundry tools or direct RPC/gRPC calls. |
| **cast** | A command-line tool from the Foundry suite used to interact with Ethereum smart contracts. BONDA uses cast extensively to query on-chain state such as role assignments, multisig configurations, and proxy implementations. |
| **Anvil** | A local Ethereum node provided by the Foundry suite. Anvil can fork mainnet state, allowing PoCs to simulate exploits against real contract deployments without affecting the live network. |
