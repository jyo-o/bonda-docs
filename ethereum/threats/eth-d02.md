# ETH-D02: Reconstruction Failure Discards All Verified Columns

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: D (Denial of Service) · **Status**: code_verified
{% endhint %}

## Overview

The Lighthouse consensus client contains a flaw in its data column reconstruction error handling. When reconstruction fails due to even a single bad data column, the implementation discards all columns associated with that reconstruction attempt, including the 64 or more columns that have already been individually verified as valid. This all-or-nothing failure mode is found in `overflow_lru_cache.rs` at lines 1360-1396.

The consequence is that a single malicious or corrupted column triggers a full re-download of approximately half the total columns for the affected slot. This creates an amplification vector where an attacker who can inject one bad column forces the victim node to perform O(N/2) additional network requests, wasting bandwidth and delaying data availability confirmation.

With the Fulu fork, data column reconstruction becomes the primary mechanism for data availability, making this a core path rather than an edge case. The elevated importance of reconstruction means this failure mode directly impacts the node's ability to confirm data availability in a timely manner.

## Prerequisites

- A malicious peer capable of propagating at least one corrupted or invalid data column
- The corrupted column must reach the victim node and be included in a reconstruction attempt
- PeerDAS must be active (post-Fulu fork)

## Attack Scenario

1. A malicious peer sends a corrupted data column to a Lighthouse node through the PeerDAS network.
2. The Lighthouse node collects data columns for a slot and begins reconstruction, including the corrupted column alongside many already-verified valid columns.
3. The reconstruction process fails because the corrupted column produces an invalid result.
4. The Lighthouse implementation in `overflow_lru_cache.rs` discards all columns for that slot, including the 64+ columns that were individually verified before reconstruction was attempted.
5. The node must re-download approximately half the total columns from the network to reattempt reconstruction.
6. The attacker can repeat this process across multiple slots, causing sustained bandwidth waste and delayed data availability confirmation.

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:M/AI:M` |
| Scope | protocol |

### Scoring Rationale

The attack vector is network-based but complexity is high because the attacker must successfully inject a corrupted column past initial validation checks. No privileges or user interaction are required. Confidentiality and integrity are unaffected as the attack targets availability only. Availability impact is medium at both node and chain levels because reconstruction is a primary path in Fulu, and repeated failures cause significant re-download overhead and data availability confirmation delays. The scope remains unchanged.

## Evidence

### Source Code

- **Repository**: Lighthouse (Sigma Prime consensus client)
- **File**: [`overflow_lru_cache.rs`, lines 1360-1396](https://github.com/sigp/lighthouse/blob/main/overflow_lru_cache.rs#L1360-L1396)
- **Finding**: When data column reconstruction fails, the entire set of columns for the affected slot is evicted from the cache, including previously verified valid columns. No mechanism exists to preserve and reuse the verified columns in a subsequent reconstruction attempt.

## Mitigations

The LRU cache eviction mechanism provides memory bounding, preventing unbounded memory growth from retained columns. However, there is no mechanism to selectively preserve verified columns when reconstruction fails. A more resilient approach would retain individually verified columns and only discard the columns that were produced during the failed reconstruction attempt. This would allow subsequent reconstruction attempts to reuse the valid columns, reducing re-download requirements from O(N/2) to just the replacement of the specific bad column.
