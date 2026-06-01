# Verification Approach

BONDA backs every finding with primary-source evidence. This page explains the verification levels, evidence sources, and cross-reference methodology.

---

## Verification Levels

Every finding is assigned one of two verification levels based on the strength of evidence collected.

| Level | Label | Meaning |
|:-----:|-------|---------|
| L3 | `poc_verified` | Attack was reproduced in a controlled environment such as an Anvil fork, an inabox deployment, or a live probe. Strongest evidence. |
| L2 | `verified` | Existence confirmed through source code analysis at a pinned commit, on-chain state queries, data measurement, or specification review. Standard level for most findings. |

```mermaid
flowchart LR
    V["🟢 verified<br/>Confirmed via code,<br/>on-chain, or measurement"]
    P["✅ poc_verified<br/>Reproduced in<br/>controlled environment"]

    V --> P

    style V fill:#57ab5a,color:#fff,stroke:#57ab5a
    style P fill:#1a7f37,color:#fff,stroke:#1a7f37
```

### Level Definitions

**`verified`** is the standard level. A finding reaches this level when its existence is confirmed through at least one concrete evidence source: tracing a vulnerable code path at a pinned commit, querying on-chain state with `cast call`, measuring live network data, or reviewing an authoritative specification against actual behavior. The distinction between static and dynamic analysis does not matter for this level — what matters is that the finding demonstrably holds.

**`poc_verified`** is the highest level. A finding reaches this level when the attack or condition is reproduced end-to-end in a controlled environment. This typically means running an exploit script on an Anvil mainnet fork, an inabox deployment, or a measured load test that demonstrates a state change, a crash, a degradation, or an unauthorized action. Reproduction provides the strongest possible evidence.

### Examples

**`verified`** — AVL-06 Deployer Admin Role (Governance Observation):
```
cast call 0x02993... "hasRole(bytes32,address)" <ADMIN> <deployer>
→ Returns: true

The deployer wallet retains admin access on mainnet.
This is confirmed on-chain state, not theoretical.
```

**`verified`** — EDA-10 Anchor Verification Disable Flag (Governance Observation):
```
Found DisableAnchorSignatureVerification flag in flags.go:251.
Default is false, but setting it to true skips all anchor checks.
The bypass path exists in source code at a pinned commit.
```

**`poc_verified`** — CEL-01 TxCache Key Mismatch (Vulnerability):
```
Reproduced on a controlled node: injected a crafted transaction that
exploited the key mismatch, growing validator memory until the node crashed.
The attack is reproducible end-to-end.
```

**`poc_verified`** — AVL-03 Kate RPC Unauthenticated KZG DoS (Vulnerability):
```
Issued concurrent kate_queryProof requests against a Kate-RPC-enabled node.
50 concurrent requests produced an 8.4x wall-time increase with no auth or
rate limit. Confirmed active on a public mainnet RPC endpoint.
```

### Distribution Across Protocols

| Protocol | Verified | PoC Verified | Total |
|----------|:--------:|:------------:|:-----:|
| EigenDA  | 11 | 3 | 14 |
| Celestia | 10 | 2 | 12 |
| Avail    | 9  | 3 | 12 |
| Ethereum | 12 | 0 | 12 |
| **Total**| **42** | **8** | **50** |

---

## Verification Process

Each finding follows a consistent verification flow. Not every finding reaches every stage — the process stops when evidence is sufficient or when access limitations prevent further confirmation.

```mermaid
flowchart LR
    A["<b>Identify</b><br/>Design analysis,<br/>spec review"] --> B["<b>Source Code<br/>Review</b><br/>Pinned commit,<br/>file + line"]
    B --> C["<b>On-Chain<br/>Verify</b><br/>cast queries,<br/>RPC calls"]
    C --> D["<b>PoC Test</b><br/>Anvil fork or<br/>live probe"]
    D --> E["<b>Cross-<br/>Reference</b><br/>≥ 2 independent<br/>sources"]

    style A fill:#e8e8e8,color:#1a1a1a,stroke:#999
    style B fill:#57ab5a,color:#fff,stroke:#57ab5a
    style C fill:#2da44e,color:#fff,stroke:#2da44e
    style D fill:#1a7f37,color:#fff,stroke:#1a7f37
    style E fill:#0d5626,color:#fff,stroke:#0d5626
```

| Stage | Action | Output |
|-------|--------|--------|
| **Identify** | Review protocol design docs, audit reports, specifications, and architecture. Flag potential attack surfaces. | Candidate finding with hypothesis. |
| **Source Code Review** | Trace the relevant code path at a pinned commit. Record file paths, line numbers, flag defaults, and control flow. | Code evidence at a specific commit hash. |
| **On-Chain Verify** | Query deployed contract state with `cast` or Substrate RPC. Confirm role assignments, parameters, and account types. | On-chain evidence at a specific block number. |
| **PoC Test** | Run a Proof of Concept on an Anvil mainnet fork or probe live endpoints with `grpcurl`. | Reproducible test or probe transcript. |
| **Cross-Reference** | Validate the finding against at least two independent sources. Confirm that evidence from different stages is consistent. | Final verification level assigned. |

---

## Evidence Sources

BONDA uses four types of primary-source evidence. All evidence is pinned to a specific commit hash or block number so that findings can be independently reproduced.

### 1. Source Code at Pinned Commits

All code references point to specific commits with file paths and line numbers.

| What We Look For | Example |
|------------------|---------|
| Flag defaults and their implications | `cli.BoolTFlag` vs. `cli.BoolFlag` in `flags.go:251` |
| Authentication and authorization paths | Presence or absence of auth middleware in handler chains |
| Deployment script omissions | Commented-out `revokeRole()` calls in `Guardian.s.sol` |
| Access control configuration | Role-based access in Solidity contracts |

**Reference format:**
```
code:disperser/cmd/apiserver/flags/flags.go:251-256
code:contracts/src/periphery/ejection/EigenDAEjectionManager.sol
```

### 2. On-Chain State via cast / RPC

Contract state is queried directly using `cast` from the Foundry toolkit or Substrate RPC calls. This captures the actual deployed configuration, not what documentation claims.

| Query Type | Command | What It Reveals |
|-----------|---------|-----------------|
| Role assignment | `cast call <contract> "hasRole(bytes32,address)" <role> <addr>` | Whether a role is actually granted |
| Role hierarchy | `cast call <contract> "getRoleAdmin(bytes32)" <role>` | Which role controls another |
| Account type | `cast code <address>` | EOA (`0x`) vs. contract (non-zero) |
| Account activity | `cast nonce <address>` | Whether the account is actively used |
| Contract parameters | `cast call <contract> "functionName()"` | Deployed thresholds, timelocks, counts |

### 3. Live Network Probes

Mainnet nodes and public endpoints are probed to confirm whether theoretical attack surfaces are exposed in production.

| Probe Type | Tool | What It Reveals |
|-----------|------|-----------------|
| gRPC service enumeration | `grpcurl <host>:443 list` | Which services are publicly exposed |
| Unauthenticated access test | `grpcurl <host>:443 <service>/<method>` | Whether endpoints require authentication |
| Validator behavior | Public APIs | Operator counts, stake distribution, infrastructure concentration |

### 4. Anvil Mainnet Fork PoC Tests

Proof of Concepts run on Anvil mainnet forks to demonstrate exploitability without affecting production systems.

| Component | Description |
|-----------|-------------|
| Fork setup | `anvil --fork-url <rpc>` at a pinned block number |
| Attack script | Shell or Python script that executes the exploit steps |
| Verification | State queries before and after to confirm the attack succeeded |

---

## Cross-Reference Methodology

Every finding must be traceable to at least two independent sources. A code comment claiming a feature exists is not evidence if on-chain state contradicts it.

| Primary Source | Cross-Referenced Against | What It Validates |
|----------------|--------------------------|-------------------|
| Source code flag default | Live probe response behavior | Whether the default actually applies in production |
| Deployment script | On-chain `hasRole` query | Whether roles were actually granted or revoked as scripted |
| Documentation claim | Source code path audit | Whether documented security features are implemented |
| Audit report fix | Current commit code review | Whether the fix was applied and remains in place |
| On-chain parameter | Source code constant | Whether the deployed value matches the intended configuration |

{% hint style="warning" %}
**Single-source findings are flagged.** If a finding can only be confirmed through one evidence type, the limitation is documented explicitly in the threat page.
{% endhint %}

---

## Example: AVL-06 — Deployer Admin Role

**Finding:** The deployer EOA for Avail's VectorX bridge contract retains `DEFAULT_ADMIN_ROLE`, enabling a solo upgrade path that bypasses multisig governance. This is a concentration of authorized control, classified as a Governance Observation.

**Verification level:** `verified` — four independent sources.

### Step 1 — On-chain role query

Three roles were checked for the deployer EOA using `cast call` against the live VectorX contract:

```
Deployer: 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e

hasRole(DEFAULT_ADMIN_ROLE, deployer) = true   ← should be false
hasRole(TIMELOCK_ROLE, deployer)      = false
hasRole(GUARDIAN_ROLE, deployer)      = false
```

### Step 2 — Role hierarchy confirmation

```
getRoleAdmin(TIMELOCK_ROLE) = 0x00   → DEFAULT_ADMIN_ROLE
```

`DEFAULT_ADMIN_ROLE` controls `TIMELOCK_ROLE`. The deployer can grant itself any role.

### Step 3 — Account type verification

```
cast code 0xDEd... = 0x       → EOA, not a multisig
cast nonce 0xDEd... = 1107    → actively used account
```

### Step 4 — Source code cross-reference

The deployment script `Guardian.s.sol` in the `sp1-vector` repository was examined. The line that should revoke `DEFAULT_ADMIN_ROLE` from the deployer is commented out. This is not a deployment accident — it is a code-level omission that persists in the repository.

### Result

The path is confirmed viable:

```
deployer → grantRole(TIMELOCK_ROLE, self) → upgradeTo(malicious_impl)
```

Four independent sources corroborate the finding: on-chain role state, role hierarchy, account type, and source code review.
