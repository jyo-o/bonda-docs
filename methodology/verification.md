# Verification Approach

BONDA backs every finding with primary-source evidence. This page explains the verification levels, evidence sources, and cross-reference methodology.

---

## Verification Levels

The key question behind every level: **where did you actually look?**

| | `code_verified` | `verified` |
|---|---|---|
| **What you looked at** | Source code on GitHub | Live mainnet contracts and endpoints |
| **What you did** | Read and traced the vulnerable code path | Ran `cast call`, `grpcurl`, or RPC queries against production |
| **What you know** | The vulnerability **exists in code** | The vulnerability **is live in production right now** |

{% hint style="info" %}
**The core distinction is static vs. dynamic analysis.** Reading source code tells you a vulnerability *could* exist. Querying mainnet tells you it *does* exist at this moment.
{% endhint %}

### Side-by-Side Example

**code_verified** — EDA-E01 (Anchor Signature Bypass):
```
Found DisableAnchorSignatureVerification flag in flags.go:251.
Default is false, but setting it to true skips all anchor checks.
→ The bypass path EXISTS in the code. Whether any live server 
  has this flag enabled is unknown.
```

**verified** — AVL-E03 (Deployer Admin Role):
```
cast call 0x02993... "hasRole(bytes32,address)" <ADMIN> <deployer>
→ Returns: true

The deployer wallet HAS admin access RIGHT NOW on mainnet.
This is not theoretical — it is a live, exploitable state.
```

---

### All Five Levels

```mermaid
flowchart LR
    U["🔘 unverified<br/>Design analysis only"]
    P["🟡 partial<br/>Some evidence,<br/>gaps remain"]
    C["🟢 code_verified<br/>Found in source code<br/><i>static analysis</i>"]
    PC["🟢 poc_verified<br/>PoC reproduced it<br/><i>controlled environment</i>"]
    V["✅ verified<br/>Confirmed on mainnet<br/><i>dynamic analysis</i>"]

    U --> P --> C --> PC --> V

    style U fill:#d4d4d4,color:#1a1a1a,stroke:#b0b0b0
    style P fill:#8ddb8c,color:#1a1a1a,stroke:#8ddb8c
    style C fill:#57ab5a,color:#fff,stroke:#57ab5a
    style PC fill:#2da44e,color:#fff,stroke:#2da44e
    style V fill:#1a7f37,color:#fff,stroke:#1a7f37
```

| Level | Label | Where You Looked | What You Did | Real Example |
|:-----:|-------|-----------------|--------------|--------------|
| ✅ | `verified` | **Live mainnet** | `cast call`, `grpcurl`, RPC query against deployed contracts or endpoints | Queried `hasRole()` on Ethereum mainnet, got `true` — deployer still has admin |
| 🟢 | `poc_verified` | **Anvil fork** | Ran a PoC script on a local mainnet fork that reproduced the attack | Forked mainnet with Anvil, called `upgradeTo(malicious)`, confirmed state change |
| 🟢 | `code_verified` | **GitHub source** | Traced the vulnerable code path at a pinned commit, recorded file and line | Found `flags.go:251` default, confirmed no auth middleware in handler chain |
| 🟡 | `partial` | **Mixed** | Some evidence exists, but access limitations block full confirmation | Docs describe a feature, but the code is in a private repo and cannot be audited |
| 🔘 | `unverified` | **Docs only** | Design-level analysis or documentation review, no code or mainnet access | KZG trusted setup ceremony — the ceremony data is not publicly auditable |

### Distribution Across Protocols

| Protocol | Verified (L4) | PoC Verified (L3) | Code Verified (L2) | Partial (L1) | Unverified (L0) |
|----------|:-------------:|:------------------:|:-------------------:|:-------------:|:---------------:|
| EigenDA  | 12 | -- | 4 | 1 | -- |
| Celestia | 4  | 2  | 5 | 1 | -- |
| Avail    | 8  | -- | -- | -- | 1 |
| Ethereum | 6  | -- | 3 | 2 | -- |

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
**Single-source findings are flagged.** If a threat can only be confirmed through one evidence type, it receives `partial` status and the limitation is documented explicitly.
{% endhint %}

---

## Example: AVL-E03 — Deployer Admin Role

**Threat:** The deployer EOA for Avail's VectorX bridge contract retains `DEFAULT_ADMIN_ROLE`, enabling a solo upgrade path that bypasses multisig governance.

**Verification level:** `verified` (Level 4) — four independent sources.

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
