# EDA-I02: BLS Private Key Exposure Through Node Process Compromise

{% hint style="info" %}
**Severity**: Medium (5.6/10) · **STRIDE**: I · **Status**: Code Verified
{% endhint %}

## Summary

The EigenDA Node process holds BLS private keys in memory during operation via the `KeyPair` field at `node.go:73`. If the Node process is compromised at the OS level, an attacker can extract the BLS private key and forge signatures for that specific operator. The root cause is in-memory plaintext key storage without hardware security module (HSM) isolation. The impact is limited to the compromised operator, as the quorum-based verification system requires aggregate signatures from multiple operators.

## Description

The Node struct holds the `KeyPair` field in process memory, exposing the BLS private key to any OS-level attacker who can read process memory.

**Source**: [`node/node.go:73`](https://github.com/Layr-Labs/eigenda/blob/ec2ce8ab/node/node.go#L73) -- Node struct holds `KeyPair` in memory.

The attack flow is:

1. Attacker compromises an EigenDA operator's host machine through OS-level exploitation.
2. Attacker extracts the BLS private key from the Node process memory.
3. Attacker uses the stolen key to forge BLS signatures, impersonating the compromised operator.
4. Forged signatures could be used to sign invalid attestations under the operator's identity.

Probe measurements detected evidence of some operator nodes being down, with `GetChunks` requests to multiple IPs (including `138.68.36.39`, `209.38.186.212`, and `146.190.207.21`) returning connection refused errors. While node downtime does not directly indicate compromise, it demonstrates that some operator nodes are not consistently available, which could indicate infrastructure weaknesses.

The impact is contained by the quorum-based verification system: protocol-level fund theft has not been demonstrated through single-operator signature forgery, as aggregate signatures from multiple operators are required.

## Proof of Concept

### Reproduction

- Code review confirmed BLS keypair is held in process memory at `node.go:73`.
- Prober detected connection refused errors from multiple operator IPs, indicating downed Node processes.
- BLS keypair storage method is an operational domain concern and cannot be externally verified beyond code inspection.
- PoC #09 cross-check confirmed the finding.

**PoC References**: #23

## Impact

Compromise of a Node process allows extraction of the operator's BLS private key, enabling signature forgery for that specific operator. The attacker can produce fraudulent attestations under the compromised operator's identity. However, the blast radius is limited to the single compromised operator: the quorum-based aggregate BLS verification system prevents a single-operator compromise from affecting the protocol's overall integrity. The attack requires physical or OS-level access to the operator's host machine, making it a targeted rather than remote attack.

### CVSS 3.1

**Score**: 5.6/10 (Medium)
**Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | P (Physical) | Node process compromise requires OS-level access to the operator's host machine |
| AC (Attack Complexity) | H (High) | An OS security breach is necessary to access process memory |
| PR (Privileges Required) | L (Low) | OS-level access to the host machine is needed |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is limited to the compromised operator |
| C (Confidentiality) | H (High) | BLS private key exposure is a critical secret leak |
| I (Integrity) | H (High) | Attacker can forge the compromised operator's signatures; however, forgery is limited to a single operator and does not affect the aggregate verification system |
| A (Availability) | N (None) | No direct availability impact from key extraction |

## Recommendation

1. Implement hardware security module (HSM) integration for BLS private key storage to prevent in-memory key exposure.
2. Consider remote signing services that keep keys off the Node host entirely.
3. Operators should follow infrastructure hardening best practices, including access controls, intrusion detection, and process isolation.
4. Implement key rotation mechanisms to limit the window of exposure if a key is compromised.
