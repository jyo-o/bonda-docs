# CEL-D15: Infinite Retry Loop Without Backoff in blob.Subscribe

{% hint style="info" %}
**Severity**: Medium · **STRIDE**: D · **Status**: code_verified
{% endhint %}

## Overview

The Subscribe method in celestia-node's blob/service.go contains an infinite retry loop that runs without any backoff or sleep when the internal getAll call fails. The pattern is a simple for loop that calls getAll and breaks only on success. If getAll returns an error, the loop immediately retries without delay, consuming 100% of the CPU core.

Under normal conditions, getAll succeeds and the loop terminates quickly. However, if a malicious full node returns intermittent errors for data requests on a specific namespace, any light node with an active subscription to that namespace enters a tight busy-loop. The context cancellation is the only exit condition, and if the subscription is long-lived, the CPU burn continues indefinitely.

This CPU exhaustion prevents the light node from performing DAS sampling and other critical operations, effectively disabling its DA verification capability.

## Prerequisites

- One malicious full node that can connect as a peer to the target light node
- The target light node must have an active namespace subscription

## Attack Scenario

1. A light node subscribes to blob updates for a specific namespace.
2. A malicious full node connects as a peer and is selected for data requests.
3. The malicious node returns intermittent errors for the subscribed namespace's data.
4. The Subscribe method's getAll call fails and immediately retries without any delay.
5. The tight loop consumes 100% of a CPU core on the light node.
6. DAS sampling and other operations are starved of CPU time, disabling DA verification.

## Impact

Light node CPU exhaustion leading to DAS sampling halt and loss of DA verification capability for that node. The attack persists until the subscription context is cancelled or the peer connection drops.

## Evidence

### Source Code

- `celestia-node/blob/service.go` -- Subscribe method contains the pattern: for { blobs, err = s.getAll(ctx, header, []Namespace{ns}); if err == nil { break } } with no sleep or backoff between retries

## Mitigations

Recommended fixes include adding exponential backoff between retries, setting a maximum retry count after which the subscription reports a permanent error, and inserting a minimum sleep interval (e.g., 100 ms) between retry attempts.
