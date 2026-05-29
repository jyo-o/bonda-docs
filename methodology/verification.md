# Verification Approach

Every BONDA finding is backed by primary-source evidence. This page describes the verification levels, source types, evidence artifacts, and cross-reference methodology used to validate threats.

---

## Verification Levels

Each threat is assigned a verification status indicating the depth of evidence supporting it:

| Level | Label | Description |
|-------|-------|-------------|
| **verified** | Full verification | PoC execution on mainnet or live system with captured evidence artifacts. The threat's exploitability has been confirmed against production infrastructure. |
| **code_verified** | Source code audit | The vulnerable code path has been traced through source code at a specific commit. Parameters, flag defaults, and control flow are confirmed, but no live exploitation was performed. |
| **poc_verified** | PoC-specific verification | A Proof of Concept demonstrates the mechanism in a controlled environment. Used primarily in Celestia analysis where mainnet probing was not performed. |
| **partial** | Partial evidence | Some evidence supports the finding, but defense boundaries or environmental factors prevent full confirmation. Acknowledged limitations are documented. |
| **unverified** | Not yet verified | The threat is identified through design analysis or documentation review but lacks primary-source confirmation. |

### Distribution Across Protocols

| Protocol | verified | code_verified | poc_verified | partial | unverified |
|----------|----------|---------------|--------------|---------|------------|
| EigenDA | 12 | 4 | -- | 1 | -- |
| Celestia | 5 | 5 | 4 | 3 | -- |
| Avail | 12 | -- | -- | -- | 2 |
| Ethereum | 6 | 3 | -- | 2 | -- |

---

## Primary Source Types

BONDA draws evidence from four categories of primary sources:

### 1. Source Code (Pinned Commits)

All code references are pinned to specific commits and include file paths with line numbers. This ensures findings remain traceable even as repositories evolve.

**What is captured:**
- Flag default values (e.g., `cli.BoolTFlag` vs. `cli.BoolFlag` and their implications)
- Control flow through authentication and authorization paths
- Presence or absence of rate limiting, validation, or access control middleware
- Commented-out code in deployment scripts (e.g., revoke operations that were disabled)

**Example reference format:**
```
code:disperser/cmd/apiserver/flags/flags.go:251-256
code:contracts/src/periphery/ejection/EigenDAEjectionManager.sol
source:github.com/availproject/sp1-vector Guardian.s.sol
```

### 2. On-Chain State

Contract state is queried directly using `cast` (from the Foundry toolkit) and Substrate RPC calls. This captures the actual deployed configuration rather than what documentation or deployment scripts claim.

**What is captured:**
- Role assignments (`hasRole`, `getRoleAdmin`, `isEjector`)
- Contract ownership and multisig configurations
- Upgrade timelock parameters
- Staking thresholds and operator counts
- Account types (EOA vs. contract) via `code` queries
- Account activity via `nonce` queries

**Example queries:**
```
cast call <contract> "hasRole(bytes32,address)" <role> <address>
cast call <contract> "getRoleAdmin(bytes32)" <role>
cast code <address>   # 0x = EOA, non-zero = contract
cast nonce <address>  # Activity indicator
```

### 3. Live Network Probes

BONDA probes mainnet nodes and public endpoints to confirm whether theoretical attack surfaces are actually exposed in production.

**What is captured:**
- gRPC service enumeration via reflection (`grpcurl ... list`)
- Endpoint authentication behavior (or lack thereof)
- Response characteristics confirming unauthenticated access
- Validator/operator behavior metrics from public APIs
- P2P network topology observations

**Example probes:**
```
grpcurl disperser.eigenda.xyz:443 list
grpcurl disperser.eigenda.xyz:443 disperser.v2.Disperser/GetBlobCommitment
```

### 4. Staking and Validator Snapshots

Operator set composition, stake distribution, and infrastructure concentration are captured at specific points in time.

**What is captured:**
- Active operator counts and stake percentages
- Nakamoto coefficients (minimum entities to reach 33%/50%/67% thresholds)
- Infrastructure provider concentration (hosting, geographic)
- Ejection/slashing event history
- Validator set overlap across roles

---

## Evidence Artifacts

Findings are supported by reproducible evidence artifacts:

| Artifact Type | Format | Purpose |
|---------------|--------|---------|
| Evidence files | YAML | Structured record of verification steps, commands, outputs, and timestamps |
| PoC scripts | Shell / Python | Reproducible proof-of-concept that demonstrates the vulnerability mechanism |
| Cast outputs | Text | Raw output from on-chain queries with block numbers for reproducibility |
| gRPC transcripts | Text | Request/response pairs from live endpoint probes |
| Staking snapshots | JSON/CSV | Point-in-time operator set data with collection timestamps |

Each evidence file includes the date of verification and the specific block number or commit hash, enabling independent reproduction.

---

## Cross-Reference Methodology

Every finding must be traceable to at least two independent sources. This guards against single-source errors — a code comment claiming a feature exists does not constitute evidence if the runtime behavior contradicts it.

**Cross-reference patterns used in BONDA:**

| Primary Source | Cross-Reference | What It Validates |
|----------------|-----------------|-------------------|
| Source code flag default | Live probe response behavior | Whether the default actually applies in production |
| Deployment script | On-chain `hasRole` query | Whether roles were actually granted/revoked as scripted |
| Documentation claim | Source code path audit | Whether documented security features are implemented |
| Audit report (resolved) | Current commit code review | Whether the fix was actually applied and remains in place |
| On-chain parameter | Source code constant | Whether the deployed value matches the intended configuration |

---

## Example: AVL-E03 — Deployer Admin Role Verification

**Threat:** The deployer EOA for Avail's VectorX bridge contract retains `DEFAULT_ADMIN_ROLE`, enabling a solo upgrade path that bypasses the intended multisig governance.

**Verification steps:**

**Step 1 — On-chain role query:**

Three roles were checked for two principals (deployer EOA and the intended admin) using `cast call` against the live VectorX contract:

```
# Deployer EOA: 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e
hasRole(DEFAULT_ADMIN_ROLE, deployer) = true    # <-- should be false
hasRole(TIMELOCK_ROLE, deployer)      = false
hasRole(GUARDIAN_ROLE, deployer)      = false
```

**Step 2 — Role hierarchy confirmation:**

```
getRoleAdmin(TIMELOCK_ROLE) = 0x00  # DEFAULT_ADMIN_ROLE
```

This confirms that `DEFAULT_ADMIN_ROLE` is the admin of `TIMELOCK_ROLE`. The deployer can grant itself any role.

**Step 3 — Account type verification:**

```
cast code 0xDEd... = 0x       # EOA (not a multisig contract)
cast nonce 0xDEd... = 1107    # Active account
```

**Step 4 — Source code cross-reference:**

The deployment script (`Guardian.s.sol`) in the `sp1-vector` repository was examined. The line that should revoke `DEFAULT_ADMIN_ROLE` from the deployer was found to be commented out — confirming this is not a deployment accident but a code-level omission that persists in the repository.

**Result:** `verified` — The attack path (deployer calls `grantRole(TIMELOCK_ROLE, self)` then `upgradeTo(malicious)`) is confirmed viable through the combination of on-chain state, role hierarchy, account type, and source code evidence. Four independent sources corroborate the finding.
