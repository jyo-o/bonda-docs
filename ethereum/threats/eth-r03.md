# ETH-R03: Prysm DataColumnsByRoot Incorrect Timeout

{% hint style="info" %}
**Severity**: Informational (no CVSS) · **STRIDE**: D (DoS) · **Status**: code\_review
{% endhint %}

## Summary

The `DataColumnsByRoot` handler uses `ttfbTimeout` (time-to-first-byte, 5 seconds) as its context timeout. The equivalent `DataColumnsByRange` handler correctly uses `respTimeout` (full response completion, 10 seconds). For large responses, the context expires at 5 seconds, causing premature response truncation and triggering peer retries that slightly amplify network load. This is a correctness/consistency defect, likely a copy-paste error, rather than a security vulnerability.

## Description

The ByRoot handler wraps its entire response transmission in a context using `ttfbTimeout`, which semantically means time until first byte. The correct constant for full response completion is `respTimeout`:

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_root.go:47
// https://github.com/prysmaticlabs/prysm
ctx, cancel := context.WithTimeout(ctx, ttfbTimeout)
// @audit ttfbTimeout (5s) used -- this context wraps the entire response transmission, so respTimeout is correct
```

For comparison, the ByRange handler uses the correct timeout:

```go
// beacon-chain/sync/rpc_data_column_sidecars_by_range.go
// https://github.com/prysmaticlabs/prysm
ctx, cancel := context.WithTimeout(ctx, respTimeout)
// @audit respTimeout (10s) -- semantically matches entire response completion
```

ByRoot responses are typically smaller than ByRange responses, so 5 seconds is often sufficient. Additionally, consensus-specs PR #3767 is moving toward deprecating TTFB/RESP timeout constants entirely.

## Proof of Concept

No exploit reproduction was conducted. The finding is established through code comparison of the two handlers' timeout constant usage.

## Impact

Large ByRoot responses are truncated when the context expires at 5 seconds. Peers receive incomplete responses and retry, causing minor network load amplification. No crash, data corruption, or consensus impact occurs.

No CVSS score is assigned. The availability impact is minor and transient, below the A:L threshold. This is classified as a correctness fix.

## Recommendation

1. Replace `ttfbTimeout` with `respTimeout` in the ByRoot handler context creation (1-line change).
2. Frame the submission as a consistency fix with ByRange, not as a security vulnerability.
3. Reference consensus-specs PR #3767 to preempt objections about the constants being deprecated.
