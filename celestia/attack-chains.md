# Celestia Attack Chains

This page documents three concrete attack chains against Celestia, constructed by composing individual threat findings. All cost estimates and parameters are sourced from on-chain data (Celestia REST API, Ethereum mainnet `cast` calls).

---

## Attack Chain A: Zero-Cost Liveness Halt

**Composed from:** CEL-G01 (KYC validator concentration and zero-cost prevote-nil censorship)

### Preconditions

| Parameter | Value | Source |
|---|---|---|
| slash_fraction_downtime | 0% | `/cosmos/slashing/v1beta1/params` |
| min_signed_per_window | 0.001 (10 of 10,000 blocks) | `/cosmos/slashing/v1beta1/params` |
| downtime_jail_duration | 60 seconds | `/cosmos/slashing/v1beta1/params` |
| Top 8 validators cumulative stake | 35.77% (> 1/3) | `/cosmos/staking/v1beta1/validators` |
| Bonded validators | 94 of 100 max | On-chain query |

### Attack Steps

1. **Coordination**: A 1/3+ cartel (minimum 8 validators) agrees to withhold prevote signatures for targeted blocks. Six of the top 8 validators are regulated entities in US/EU/Swiss/HK jurisdictions -- a single court order could compel compliance without malicious intent.

2. **Execution**: Cartel members send prevote-nil for every proposed block. Since 2/3 prevotes are required for precommit, consensus stalls. The proposer rotates on timeout, but every new proposal is also nil-voted.

3. **Persistence**: Each cartel member signs 10 out of every 10,000 blocks to stay above the min_signed_per_window threshold and avoid jail. Even if jailed, downtime_jail_duration is 60 seconds -- they rejoin almost immediately.

4. **No evidence trail**: There is no nil-vote evidence type in celestia-core (evidence.go implements only DuplicateVoteEvidence and LightClientAttackEvidence). Honest and malicious prevote-nil are indistinguishable at the protocol level.

### Cost

| Component | Amount |
|---|---|
| On-chain slashing | **$0** (slash_fraction_downtime = 0%) |
| Opportunity cost | ~$139K/day in forgone staking rewards (at ~10% APR) |
| Social cost | Reputation damage (not quantifiable) |

### Impact

- Celestia mainnet halts: no new blocks finalized.
- All rollups using Celestia DA (Eclipse, Manta, etc.) cannot post new data.
- Blobstream stops updating: Ethereum-side DA verification ceases.
- L2 sequencer queues back up; bridge withdrawals are delayed.

---

## Attack Chain B: Blobstream Relayer SPOF

**Composed from:** CEL-E01 (SP1Blobstream multisig), Blobstream relayer architecture

### Preconditions

| Parameter | Value | Source |
|---|---|---|
| Active relayer | 1 EOA (0x9c0B...afDC) | `cast call` approvedRelayers |
| checkRelayer | true (permissioned mode) | `cast call` on SP1Blobstream |
| Guardian | 4-of-6 Gnosis Safe (0x8bF3...18E6) | `cast call` getThreshold/getOwners |
| Commit interval | ~80-130 minutes | Transaction timestamp analysis |
| ZK proof dependency | Succinct Labs SP1 prover network | SP1Blobstream architecture |

### Attack Steps

1. **Relayer compromise**: The single approved relayer EOA (0x9c0B...afDC) is taken offline. This can occur via private key theft, server infrastructure failure, legal action against the operator (likely Succinct Labs), or DDoS.

2. **Attestation halt**: `commitHeaderRange()` calls cease. No new `DataCommitmentStored` events are emitted on Ethereum.

3. **L2 impact**: Any L2 that depends on Blobstream for DA verification (e.g., `verifyAttestation()` calls) can no longer confirm new Celestia blocks from Ethereum. Settlement and finality are disrupted.

4. **Recovery blocked**: Even if checkRelayer were switched to false (permissionless mode), independent relayer operation requires access to Succinct Labs' SP1 prover network and the correct `blobstreamProgramVkey`. This creates a double SPOF.

### Timeline

| Time After Relayer Down | Effect |
|---|---|
| t+0 | Last successful commit (latestBlock frozen) |
| t+~100 min | First missed commit window |
| t+~200 min | Second miss, gap grows to ~830 blocks |
| t+~17 hours | 10,000 block gap exceeds DATA_COMMITMENT_MAX, batch splitting required for recovery |

### Impact

- All Blobstream-dependent L2s lose Ethereum-side DA verification.
- Celestia chain itself continues producing blocks normally -- the SPOF is only in the Ethereum attestation path.
- The 4-of-6 guardian multisig can freeze the contract but cannot relay attestations.

---

## Attack Chain C: Coordinated Safety Violation

**Composed from:** CEL-G01 (validator concentration)

### Preconditions

| Parameter | Value | Source |
|---|---|---|
| slash_fraction_double_sign | 0.02 (2%) | `/cosmos/slashing/v1beta1/params` |
| Top 28 validators cumulative stake | 67.02% (> 2/3) | `/cosmos/staking/v1beta1/validators` |
| Top 28 total stake | ~340.6M TIA | On-chain calculation |
| TIA price | $0.468 | CoinGecko (2026-05-26) |
| Correlation penalty | None (Cosmos SDK flat per-validator slashing) | Cosmos SDK x/slashing source |

### Attack Steps

1. **Cartel formation**: 28 validators controlling >2/3 of voting power coordinate to execute a double-sign attack. This requires agreement across 28 independent entities.

2. **Double signing**: The cartel signs two conflicting blocks at the same height, creating a chain fork.

3. **Exploitation**: On one fork branch, the attacker executes profitable transactions (double-spend, bridge exploits, oracle manipulation).

4. **Slashing**: Each participating validator is slashed 2% of their individual stake. Total on-chain cost: ~6.8M TIA (~$3.19M at $0.468/TIA).

5. **Tombstoning**: Slashed validators are permanently ejected (tombstoned), but the attack profit has already been realized. New validator identities can be created if max_validators has capacity.

### Cost Comparison

| Chain | Safety Violation Cost | Mechanism |
|---|---|---|
| **Celestia** | ~$3.19M (2% flat slash, no correlation penalty) | Double sign, 28 validators |
| Cosmos Hub | ~$10M+ (5% double sign slash) | Double sign |
| Ethereum PoS | ~$13B+ (1/3 stake slash + correlation penalty) | Slashing with correlation amplifier |

Celestia's safety violation cost is approximately 4,000x cheaper than Ethereum's for an equivalent 2/3 attack, because Cosmos SDK applies a flat 2% penalty regardless of how many validators participate simultaneously. Ethereum's correlation penalty causes slashing to approach 100% when many validators are slashed in the same time window.

### Practical Feasibility

While the on-chain cost is low, practical barriers remain significant:
- Coordinating 28 independent entities carries high coordination cost and internal defection risk.
- Double-signing itself does not produce direct revenue -- a separate exploitation mechanism (bridge exploit, short position) is required.
- Tombstoning is permanent, destroying the validators' long-term staking positions.

---

## Summary Matrix

| Attack Chain | On-Chain Cost | Impact Scope | Minimum Entities | Assessment |
|---|---|---|---|---|
| A: Liveness Halt | $0 | Celestia + all dependent L2s | 8 validators | Highest risk: zero cost, broad impact |
| B: Blobstream SPOF | Infrastructure attack cost | L2 DA verification only | 1 EOA | Highest likelihood: single point of failure |
| C: Safety Violation | ~$3.19M | Chain fork, double-spend | 28 validators | Lowest likelihood: high coordination cost |
