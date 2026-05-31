# Verification Approach

BONDA backs every finding with primary-source evidence. This page explains the verification levels, evidence sources, and cross-reference methodology.

---

## Verification Levels

Every threat is assigned one of three verification levels based on the strength of evidence collected.

| Level | Label | Meaning |
|:-----:|-------|---------|
| L3 | `poc_verified` | Attack was reproduced in a controlled environment such as an Anvil fork or testnet. Strongest evidence. |
| L2 | `verified` | Vulnerability existence confirmed through source code analysis, on-chain state queries, data measurement, or documentation review. Standard level for most findings. |
| L1 | `unverified` | Implementation does not yet exist or access is insufficient for verification. Design-level analysis only. |

```mermaid
flowchart LR
    U["🔘 unverified<br/>Design analysis only"]
    V["🟢 verified<br/>Confirmed via code,<br/>on-chain, or measurement"]
    P["✅ poc_verified<br/>Reproduced in<br/>controlled environment"]

    U --> V --> P

    style U fill:#d4d4d4,color:#1a1a1a,stroke:#b0b0b0
    style V fill:#57ab5a,color:#fff,stroke:#57ab5a
    style P fill:#1a7f37,color:#fff,stroke:#1a7f37
```

### Level Definitions

**`verified`** is the standard level. A finding reaches this level when its existence is confirmed through at least one concrete evidence source: tracing a vulnerable code path at a pinned commit, querying on-chain state with `cast call`, measuring live network data, or reviewing authoritative documentation against actual behavior. The distinction between static and dynamic analysis does not matter for this level — what matters is that the vulnerability demonstrably exists.

**`poc_verified`** is the highest level. A finding reaches this level when the attack is reproduced end-to-end in a controlled environment. This typically means running an exploit script on an Anvil mainnet fork that demonstrates a state change, a crash, or an unauthorized action. PoC reproduction provides the strongest possible evidence.

**`unverified`** applies when the target implementation does not yet exist or when access is insufficient to confirm the finding. The analysis is based on design documents, specifications, or architectural reasoning. The threat may be valid, but evidence cannot be gathered until the implementation is available.

### Examples

**`verified`** — AVL-E03 Deployer Admin Role:
```
cast call 0x02993... "hasRole(bytes32,address)" <ADMIN> <deployer>
→ Returns: true

The deployer wallet has admin access on mainnet.
This is confirmed on-chain state, not theoretical.
```

**`verified`** — EDA-E01 Anchor Signature Bypass:
```
Found DisableAnchorSignatureVerification flag in flags.go:251.
Default is false, but setting it to true skips all anchor checks.
The bypass path exists in source code at a pinned commit.
```

**`poc_verified`** — CEL-D17 TxCache Key Mismatch:
```
Reproduced on Anvil fork: injected a crafted transaction that
exploited the key mismatch, causing a validator crash.
The attack is reproducible end-to-end.
```

**`unverified`** — hypothetical example:
```
Target implementation does not yet exist. Only design documents
are available. The threat is identified from specification analysis,
but no code or deployed system is available for verification.
```

### Distribution Across Protocols

| Protocol | Verified | PoC Verified | Unverified |
|----------|:--------:|:------------:|:----------:|
| EigenDA  | 13 | 0 | 0 |
| Celestia | 10 | 2 | 0 |
| Avail    | 9  | 0 | 0 |
| Ethereum | 4  | 0 | 0 |

---

## Verification Process

Each threat follows a consistent verification flow. Not every threat reaches every stage — the process stops when evidence is sufficient or when access limitations prevent further confirmation.

```mermaid
flowchart LR
    A["<b>Identify</b><br/>Design analysis,<br/>docs review"] --> B["<b>Source Code<br/>Review</b><br/>Pinned commit,<br/>file + line"]
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
| **Identify** | Review protocol design docs, audit reports, and architecture. Flag potential attack surfaces. | Candidate threat with hypothesis. |
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
**Single-source findings are flagged.** If a threat can only be confirmed through one evidence type, the limitation is documented explicitly in the threat page.
{% endhint %}

---

## Example: AVL-E03 — Deployer Admin Role

**Threat:** The deployer EOA for Avail's VectorX bridge contract retains `DEFAULT_ADMIN_ROLE`, enabling a solo upgrade path that bypasses multisig governance.

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

The attack path is confirmed viable:

```
deployer → grantRole(TIMELOCK_ROLE, self) → upgradeTo(malicious_impl)
```

Four independent sources corroborate the finding: on-chain role state, role hierarchy, account type, and source code review.
