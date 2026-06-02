# Verification Approach

BONDA backs every finding with primary-source evidence. This page explains the verification levels and the verification process.

---

## Verification Levels

Every finding is assigned one of two verification levels based on the strength of evidence collected.

| Level | Label | Meaning |
|:-----:|-------|---------|
| L2 | `poc_verified` | Attack was reproduced in a controlled environment such as an Anvil fork, an inabox deployment, or a live probe. Strongest evidence. |
| L1 | `verified` | Existence confirmed through source code analysis at a pinned commit, on-chain state queries, data measurement, or specification review. Standard level for most findings. |

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
| Ethereum | 12 | 0 | 12 |
| EigenDA  | 11 | 3 | 14 |
| Celestia | 10 | 2 | 12 |
| Avail    | 9  | 3 | 12 |
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
