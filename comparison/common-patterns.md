# Common Threat Patterns Across DA Layers

Six structural threat patterns recur across multiple DA protocols. These are not coincidences — they reflect shared architectural constraints in how DA layers bridge trust to Ethereum and incentivize honest behavior.

{% hint style="info" %}
Each pattern links to the specific threats that demonstrate it. Click any threat ID to see the full analysis with evidence.
{% endhint %}

## Pattern 1: Relayer / Bridge Single Point of Failure

Every DA protocol that bridges attestations to Ethereum relies on a small number of relayers, and in most cases, a single EOA.

| Protocol | Threat ID | Relayer Configuration | Fallback |
|---|---|---|---|
| EigenDA | EDA-04 | 1 relay registered on-chain (RelayRegistry nextRelayKey=1) | GetChunks direct retrieval (post-failure) |
| Avail | AVL-04 | 1 approved relayer EOA (0x27BF...787D), checkRelayer=true | None. No on-chain heartbeat or staleness detection |
| Celestia | CEL-09 | 1 active relayer EOA (0x9c0B...afDC) for SP1Blobstream | Guardian (4-of-6) can freeze but not relay |

All three protocols exhibit the same failure mode: if the single relayer goes offline, DA attestations stop flowing to Ethereum. The impact varies:

- **EigenDA** has a validator direct retrieval fallback (GetChunks), but it activates only after relay failure is detected.
- **Avail** has no on-chain staleness detection at all -- SP1Vector.sol contains zero references to `block.timestamp` in `commitHeaderRange()`, no cooldown, no heartbeat. The relayer client (operator.rs) controls timing with LOOP_INTERVAL_MINS=60, but this has no on-chain enforcement.
- **Celestia** Blobstream is additionally constrained by SP1 ZK proof generation dependency on Succinct Labs' prover network, creating a double SPOF.

## Pattern 2: Multisig Concentration and Overlap

Governance power across DA protocols is concentrated in small multisigs, often without timelocks and sometimes with key holder overlap.

| Protocol | Threat ID | Multisig | Controls | Timelock |
|---|---|---|---|---|
| EigenDA | EDA-07 | 3-of-4 Gnosis Safe (0x002721...) | 8 core contracts (ServiceManager, RegistryCoordinator, EjectionManager, ThresholdRegistry, RelayRegistry, DisperserRegistry, PaymentVault, CertVerifierRouter) | None |
| Avail | AVL-08 | 4-of-7 Gov + 3-of-5 Pauser + 2-of-3 SP1 | 4/5 Pauser signers overlap with Gov signers; 1 signer (0x72Ff...) participates in all 3 multisigs | Bridge: 24h. VectorX: None |
| Celestia | CEL-09 | 4-of-6 Gnosis Safe (0x8bF3...18E6) | SP1Blobstream: GUARDIAN + TIMELOCK + DEFAULT_ADMIN all assigned to same multisig | None |

Key observations:
- **EigenDA**: All 4 signers are EOAs with no ENS or on-chain identity. 3 key compromises give full control over the entire protocol governance with no delay.
- **Avail**: The triple overlap of key holder 0x72Ff... across Gov, Pauser, and SP1VerifierGateway means a single key compromise degrades the effective independence of all three multisigs.
- **Celestia**: The `initialize(guardian, guardian)` pattern in SP1Blobstream assigns the same address to `_timelock` and `_guardian`, collapsing role separation.

## Pattern 3: Governance Centralization

Beyond multisig structure, broader governance centralization appears across protocols.

| Protocol | Threat ID | Issue |
|---|---|---|
| Celestia | CEL-08 | Top 8 validators hold 35.77% (>1/3 threshold). 6 of 8 are KYC-regulated entities. Single court order could force prevote-nil censorship. max_validators=100 with 94 bonded (near saturation). |
| EigenDA | EDA-09 | Q0 top 3 operators hold 39.8% (>33% safety threshold). Q2 has AltLayer at 52.6% solo. Coinbase suspected to control 5 of top 4-8 in Q1. |
| Avail | AVL-06 | Deployer EOA (0xDEd0...E18e) retains DEFAULT_ADMIN_ROLE. Can solo grant TIMELOCK_ROLE to self and upgrade VectorX in 2 transactions. |

## Pattern 4: Missing or Dormant Slashing

No DA protocol assessed has effective economic penalties for operator misbehavior in production.

| Protocol | Threat ID | Slashing Status | Consequence |
|---|---|---|---|
| EigenDA | EDA-11 | Not implemented. Zero slash/freeze functions in core contracts. AllocationManager OperatorSetCount=0. 500K blocks with 0 slash events. | Operators can sign attestations without storing data (free-riding). 11 dead operators observed. |
| Avail | AVL-11 | Infrastructure exists in code (67 runtime metadata references). 688 eras with 0 slashes applied (UnappliedSlashes=empty). | Slashing is technically possible but has never been triggered. No economic deterrent demonstrated. |
| Celestia | CEL-08 | slash_fraction_downtime=0%. min_signed_per_window=0.001 (10/10,000 blocks). | 1/3 cartel can halt the chain at zero on-chain cost. |

The pattern is consistent: DA layers prioritize network growth over economic security enforcement. This creates an asymmetric incentive structure where operators earn rewards without risk of penalty for misbehavior.

## Pattern 5: No Data Availability Sampling (or Incomplete)

DAS is the theoretical foundation for trust-minimized DA verification, but implementation status varies dramatically.

| Protocol | Threat ID | DAS Status |
|---|---|---|
| EigenDA | EDA-12 | **No DAS by design.** Spec explicitly states DAS is not used. Clients must trust the quorum's BLS aggregate signature (55% stake threshold). Client-side random shuffle is load balancing, not cryptographic sampling. |
| Avail | AVL-12 | **DAS implemented, reconstruction incomplete.** Light client DAS achieves 99.84% confidence (Observatory measured). However, block reconstruction protocol is still in development -- full recovery from DAS samples alone is not yet possible. |
| Celestia | CEL-11 | **DAS-only model after BEFP removal.** BEFP (Bad Encoding Fraud Proofs) were removed as dead code in PR #4934 (April 2026). Light nodes now rely solely on 16-sample DAS for availability, with no correctness verification. Documentation still claims BEFP+DAS model. |
| Ethereum | ETH-10, ETH-11 | **PeerDAS active since the Fusaka fork.** Column-based custody with DataColumnSidecars. Erasure coding is currently one-dimensional (ETH-10), and fork choice gates block import on custody, not on a completed sampling query (ETH-11) -- so the trust-minimized sampling path is not yet the security-critical gate. |

## Pattern 6: KZG Trusted Setup Risks

KZG-based protocols share exposure to trusted setup assumptions.

| Protocol | Threat ID | Setup Ceremony | Risk |
|---|---|---|---|
| Ethereum | ETH-02 | Ethereum KZG ceremony | `load_trusted_setup` deserializes G1/G2 points without subgroup membership checks, creating a validation asymmetry with the runtime input path. Risk is limited to build-time supply chain compromise. |

The setup relies on the 1-of-N honest participant assumption, and Ethereum's implementation embeds setup bytes at build time, preventing runtime tampering.
