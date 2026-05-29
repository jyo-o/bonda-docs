# ETH-S02: Custody Group Node ID Grinding

{% hint style="info" %}
**Severity**: Low (3.5/10) · **STRIDE**: S (Spoofing) · **Scope**: protocol · **Status**: code_verified
{% endhint %}

## Overview

In PeerDAS, custody group assignment is based on node_id. An attacker can brute-force generate node_ids that concentrate on specific data column sets, threatening the availability of those columns. With Fulu fork activating PeerDAS, custody groups become an actual security boundary, increasing the impact.

## Prerequisites

Significant computing resources for brute-force node_id generation

## Attack Scenario

**Condition**: PeerDAS custody group assignment via node_id

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 3.5/10 (Low) |
| BVSS Vector | `B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/CI:N/I:N/II:N/A:M/AI:M` |
| Likelihood | Low |
| Scope | protocol |
| Target | Process |

## Code References

*No specific code references provided.*

## Verification & Evidence

**Status**: code_verified

Confirmed PeerDAS custody group assignment logic is node_id-based in code.

## Mitigations

The custody group count is sufficiently large, and grinding cost relative to node count makes practical attack difficulty high.
