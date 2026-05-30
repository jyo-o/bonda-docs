# EDA-I02: BLS Private Key Exposure Through Node Process Compromise

{% hint style="info" %}
**Severity**: Low (2.8/10) · **STRIDE**: I · **Status**: Code Verified
{% endhint %}

## Overview

The EigenDA Node process holds BLS private keys in memory during operation. If the Node process is compromised at the OS level, an attacker can extract the BLS private key and forge signatures for that specific operator. This would allow the attacker to produce fraudulent attestations under the compromised operator's identity.

Probe measurements detected evidence of some operator nodes being down, with `GetChunks` requests to multiple IPs (including `138.68.36.39`, `209.38.186.212`, and `146.190.207.21`) returning connection refused errors. While node downtime does not directly indicate compromise, it demonstrates that some operator nodes are not consistently available, which could indicate infrastructure weaknesses.

The impact is limited to the compromised operator. Protocol-level fund theft has not been demonstrated through single-operator signature forgery, as the quorum-based verification system requires aggregate signatures from multiple operators.

## Prerequisites

- Compromise of the Node process at the OS level, requiring the attacker to breach the host machine's security.

## Attack Scenario

1. An attacker compromises an EigenDA operator's host machine through OS-level exploitation.
2. The attacker extracts the BLS private key from the Node process memory (stored in the `KeyPair` field at `node.go:73`).
3. The attacker uses the stolen key to forge BLS signatures, impersonating the compromised operator.
4. The forged signatures could be used to sign invalid attestations under the operator's identity.
5. The impact is limited to the single compromised operator; other verification layers (quorum thresholds, aggregate BLS verification) contain the blast radius.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 2.8/10 (Low) |
| BVSS Vector | `BVSS:1.1/B:N/AV:P/AC:H/PR:R/UI:N/S:U/C:H/I:H/A:N/CI:H/II:M/AI:N` |
| Scope | Protocol |

### Scoring Rationale

Blockchain Impact (B) is None because a protocol-level fund theft path through single-operator signature forgery has not been demonstrated. Attack Vector (AV) is Physical because Node process compromise requires OS-level access. Attack Complexity (AC) is High because an OS security breach is necessary. Confidentiality impact (C) is High and Confidentiality Infrastructure impact (CI) is also High because BLS private key exposure is a serious secret leak. Integrity impact (I) is High because the attacker can forge the compromised operator's signatures, but Integrity Infrastructure impact (II) is Medium because the forgery is limited to a single operator and does not affect the aggregate verification system.

## Evidence

### Source Code

- [`node/node.go:73`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/node/node.go#L73) -- Node struct holds `KeyPair` in memory.

### PoC Testing

- Code review confirmed BLS keypair is held in process memory at `node.go:73`.
- Prober detected connection refused errors from multiple operator IPs, indicating downed Node processes.
- BLS keypair storage method is an operational domain concern and cannot be externally verified beyond code inspection.
- PoC #09 cross-check confirmed the finding.

**PoC References**: #23

## Mitigations

Process-level security at the OS layer is the primary defense. Operators should follow infrastructure hardening best practices, including access controls, intrusion detection, and secure key management. Hardware security modules (HSMs) or remote signing services could prevent in-memory key exposure.
