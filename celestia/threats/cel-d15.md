# CEL-D15: Infinite Retry Loop Without Backoff in blob.Subscribe

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Summary

The `Subscribe` method in celestia-node's `blob/service.go` contains an infinite retry loop that runs without any backoff or sleep when the internal `getAll` call fails. If a malicious full node returns intermittent errors for data requests on a specific namespace, any light node with an active subscription to that namespace enters a tight busy-loop consuming 100% of a CPU core, preventing DAS sampling and other critical operations.

## Description

The retry loop in the `Subscribe` method uses a bare `for` loop with no delay between iterations:

```go
// celestia-node/blob/service.go
// @audit Subscribe method contains the pattern:
// for {
//     blobs, err = s.getAll(ctx, header, []Namespace{ns})
//     if err == nil { break }
// }
// @audit No sleep or backoff between retries — immediate retry on failure
```

Under normal conditions, `getAll` succeeds and the loop terminates quickly. However, when a malicious full node returns intermittent errors:

1. The light node has an active namespace subscription
2. A malicious full node connects as a peer and is selected for data requests
3. The malicious node returns intermittent errors for the subscribed namespace
4. The `getAll` call fails and the loop immediately retries without any delay
5. The tight loop consumes 100% of a CPU core

The only exit condition is context cancellation. If the subscription is long-lived, the CPU burn continues indefinitely. This CPU exhaustion prevents the light node from performing DAS sampling and other critical operations, effectively disabling its DA verification capability.

## Proof of Concept

No proof of concept was conducted for this threat.

## Impact

Light node CPU exhaustion leading to DAS sampling halt and loss of DA verification capability for that node. The attack persists until the subscription context is cancelled or the peer connection drops.

### CVSS 3.1

**Score**: 5.9/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Malicious full node connects over the P2P network |
| AC (Attack Complexity) | H (High) | Requires the malicious node to be selected as the data peer for the specific subscribed namespace |
| PR (Privileges Required) | N (None) | No privileges required; any full node peer can return errors |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted light node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | H (High) | 100% CPU burn disables DAS sampling and all critical operations on the light node |

## Recommendation

1. Add exponential backoff between retries (e.g., starting at 100ms, doubling up to a maximum of 30 seconds).
2. Set a maximum retry count after which the subscription reports a permanent error to the caller.
3. Insert a minimum sleep interval (e.g., 100ms) between retry attempts as an immediate fix.
