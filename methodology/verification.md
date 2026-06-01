# Verification Approach

BONDA backs every finding with primary-source evidence. This page explains the verification levels, evidence sources, and cross-reference methodology.

***

## Verification Levels

Every threat is assigned one of three verification levels based on the strength of evidence collected.

| Level | Label          | Meaning                                                                                                                                                       |
| :---: | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|   L2  | `poc_verified` | Attack was reproduced in a controlled environment such as an Anvil fork or testnet. Strongest evidence.                                                       |
|   L1  | `verified`     | Threat existence confirmed through source code analysis, on-chain state queries, data measurement, or documentation review. Standard level for most findings. |

```mermaid
flowchart LR
    V["🟢 verified<br/>Confirmed via code,<br/>on-chain, or measurement"]
    P["✅ poc_verified<br/>Reproduced in<br/>controlled environment"]

    V --> P

    style V fill:#57ab5a,color:#fff,stroke:#57ab5a
    style P fill:#1a7f37,color:#fff,stroke:#1a7f37
```

### Level Definitions

**`verified`** is the standard level. A finding reaches this level when its existence is confirmed through at least one concrete evidence source: tracing a vulnerable code path at a pinned commit, querying on-chain state with `cast call`, measuring live network data, or reviewing authoritative documentation against actual behavior. The distinction between static and dynamic analysis does not matter for this level — what matters is that the vulnerability demonstrably exists.

**`poc_verified`** is the highest level. A finding reaches this level when the attack is reproduced end-to-end in a controlled environment. This typically means running an exploit script on an Anvil mainnet fork that demonstrates a state change, a crash, or an unauthorized action. PoC reproduction provides the strongest possible evidence.

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

### Distribution Across Protocols

| Protocol | Verified | PoC Verified |
| -------- | :------: | :----------: |
| Ethereum |     4    |       0      |
| EigenDA  |    13    |       0      |
| Celestia |    10    |       2      |
| Avail    |     9    |       0      |

