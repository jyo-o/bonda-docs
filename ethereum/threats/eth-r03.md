# ETH-R03: Prysm DataColumnsByRoot Incorrect Timeout

{% hint style="info" %}
**Severity**: Informational (no CVSS) · **STRIDE**: D (DoS) · **Status**: code\_review
{% endhint %}

## Summary

The `DataColumnsByRoot` handler uses `ttfbTimeout` (time-to-first-byte, 5 seconds) as its context timeout. The equivalent `DataColumnsByRange` handler correctly uses `respTimeout` (full response completion, 10 seconds). For large responses, the context expires at 5 seconds, causing premature response truncation and triggering peer retries that slightly amplify network load. This is a **correctness/consistency defect (likely copy-paste error)** rather than a security vulnerability -- no crash, data corruption, or consensus impact occurs.

## Description

### Vulnerable Code -- ByRoot Handler (wrong timeout)

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_root.go:47
// https://github.com/prysmaticlabs/prysm
ctx, cancel := context.WithTimeout(ctx, ttfbTimeout)
// @audit ttfbTimeout (5s) used -- this context wraps the entire response transmission, so respTimeout is correct
// @audit semantic mismatch: "5s until first byte" vs actual usage: "entire response completion"
```

### Correct Pattern -- ByRange Handler (for comparison)

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_range.go
// https://github.com/prysmaticlabs/prysm
ctx, cancel := context.WithTimeout(ctx, respTimeout)
// @audit respTimeout (10s) -- semantically matches "entire response completion"
```

### Root Cause

`ttfbTimeout` means "time until first byte"; `respTimeout` means "time for complete response." A context wrapping the entire response transmission should use `respTimeout`. The ByRoot handler's use of `ttfbTimeout` is a **semantic misuse (likely copy-paste error)**.

### Critical Limitation

- ByRoot responses are typically smaller than ByRange responses, so 5 seconds is often sufficient.
- Consensus-specs **PR #3767** is moving toward deprecating TTFB/RESP timeout constants, meaning the constants themselves may be removed.

### STRIDE Detail

| Category | Relevance | Analysis |
|----------|-----------|----------|
| **D -- DoS** | **Primary** (minor) | Large ByRoot responses truncated early at 5s, causing peer retries and minor load amplification |

## Proof of Concept

No exploit reproduction was conducted. The finding is established through **code comparison** of the two handlers' timeout constant usage -- no separate proof of concept is necessary.

## Impact

1. Large ByRoot responses (many columns requested) are truncated when the context expires at 5 seconds
2. Peers receive incomplete responses and retry
3. Minor network load amplification from retries
4. **No cascade.** No crash, data corruption, or consensus impact

No meaningful CVSS score is assigned. The availability impact is minor and transient, below the A:L threshold. This item is classified as a **correctness fix**, not a security finding.

## Recommendation

Replace the timeout constant (1-line change):

```go
// [Before]
ctx, cancel := context.WithTimeout(ctx, ttfbTimeout)

// [After]
ctx, cancel := context.WithTimeout(ctx, respTimeout)   // ttfbTimeout -> respTimeout
```

**Submission framing:** Present as "a 1-line fix for behavioral consistency with ByRange," not as a security vulnerability. Reference consensus-specs PR #3767 (TTFB/RESP deprecation) to preempt "this will be removed anyway" objections.
