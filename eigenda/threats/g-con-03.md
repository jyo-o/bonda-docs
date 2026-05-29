# G-CON-03: Operator Infrastructure (Cloud/ASN) Concentrated in Few Hosting Providers

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **STRIDE**: CON · **Scope**: protocol · **Status**: Verified
{% endhint %}

## Overview

78 operator host classes extracted (72 raw IP mappings) -> ASN aggregation. Q0 stake: AWS 21.78%, OVH 15.67%, Hetzner, etc. -- top 5 cumulative 82.7%. Q1 stake: Herd SaaS alone 41.87%. A single cloud region/provider outage could bring quorum confirmation threshold (55%) within reach.

## Prerequisites

Multiple operators using the same cloud provider/ASN

## Attack Scenario

Herd SaaS Q1 41.87%

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | 5.3/10 (Medium) |
| BVSS Vector | `BVSS:1.1/B:N/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/CI:N/II:N/AI:M` |
| Likelihood | Unrated |
| Scope | protocol |
| Target | Process, Datastore |

### BVSS Rationale

B:N -- No financial impact. AC:H -- Requires specific provider failure conditions. A:H/AI:M -- AWS 21.78% Q0, Herd SaaS 41.87% Q1, top5 cumulative 82.7%; single provider outage approaches quorum confirmation 55% threshold but is transient.

## Code References


### PoC Notes

- poc/18-cloud-asn-concentration/evidence.yaml

### Other References

- ipinfo.io ASN lookup [VERIFIED]

## Verification & Evidence

**Status**: Verified

AWS 21.78% Q0, Herd SaaS 41.87% Q1. Top5 cumulative Q0=82.7%.

**PoC References**: #16

## Mitigations

Geographic/provider diversity incentives, on-prem node supplementation.
