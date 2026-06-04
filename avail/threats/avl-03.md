# AVL-03: Kate RPC Triggers Unauthenticated KZG Computation Without Rate Limiting

{% hint style="info" %}
**Severity**: Medium (5.3/10) · **Likelihood**: Very High · **Category**: Vulnerability · **Status**: poc_verified
{% endhint %}

## Summary

The Avail full node Kate RPC endpoints `kate_queryProof`, `kate_queryMultiProof`, and `kate_queryRows` trigger KZG proof computation without authentication. No rate limiting exists at the handler level, the polynomial grid is reconstructed on every request with no caching, and proof generation runs across all CPU cores through `rayon`. Kate RPC is disabled by default, but it is enabled on the public mainnet RPC `mainnet-rpc.avail.so`, and any node serving light-client data availability sampling must enable it, so a reachable attack surface exists.

## Description

![AVL-03 data flow — Avail Read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/avail/assets/dfd/avail-read.png)

*Data flow — Avail Read: Full Node.*

Each `kate_queryProof` call drives the server through the full proof pipeline with no per-request reuse of prior work.

```rust
// runtime/src/kate/native.rs
// @audit proof generation runs over all CPU cores via rayon with no concurrency cap
// https://github.com/availproject/avail/blob/main/kate/src/gridgen/mod.rs
let proofs: Vec<_> = cells.into_par_iter()
    .map(|cell| poly.proof(srs, &cell))
    .collect();
```

The per-request path loads the block extrinsics, reconstructs the data matrix with `EGrid::from_extrinsics()`, extends columns for erasure coding, builds the polynomial grid, and generates a KZG proof per requested cell over BLS12-381. The polynomial grid is rebuilt on every call, so repeated requests against the same block repeat the entire computation.

```rust
// node/src/cli.rs
// @audit Kate RPC is gated by a flag but carries no handler-level rate limiting; enabled on public mainnet RPC
// https://github.com/availproject/avail/blob/main/node/src/cli.rs
#[clap(long = "enable-kate-rpc", default_value_t = false)]
pub kate_rpc_enabled: bool,
```

Substrate's `--rpc-rate-limit` is disabled by default, applies per connection rather than per IP, treats every method uniformly, and can be sidestepped with JSON-RPC batch requests. The Kate handlers themselves apply no throttling, queueing, or limit on concurrent computation.

The endpoint is confirmed reachable without authentication on mainnet: `kate_blockLength` and `kate_queryProof` both return valid results from `mainnet-rpc.avail.so` over plain HTTP with no credentials.

## Proof of Concept

The asymmetry was measured on a native x86 GCP host (n2-standard-16, 16 vCPU, not emulated) against a self-hosted node serving a full 4 MB block (256 x 512 grid), using `perf` for CPU-time.

- **One cheap request forces a full grid build**: a single 1-cell `kate_queryProof` on the 4 MB block costs 0.197 core-seconds (median wall 197.9 ms, one core fully busy).
- **Cost is independent of cells requested**: 1 cell and 64 cells cost almost the same (199 ms vs 269 ms), so the grid build dominates and per-cell extraction is negligible.
- **No caching**: repeated requests with distinct cells all cost ~199 ms; every request rebuilds the grid.
- **Linearly stackable to saturation**: node CPU scales at ~100% per connection; ~16 unauthenticated connections pin all 16 cores, after which co-tenant RPC latency degrades ~1180x, with a sub-millisecond `system_health` check taking over a second.
- **Mainnet exposure**: `kate_queryProof` is reachable without authentication on `mainnet-rpc.avail.so`.

The per-request cost is modest in absolute terms, around 0.2 core-seconds and roughly 70x cheaper than the EigenDA GetBlobCommitment path; the severity is the asymmetry and the absence of any handler-level rate limit, not a single-request kill.

See [Verification Evidence](../evidence.md#kate-rpc-unauthenticated-kzg-computation-avl-03) for the full setup, perf measurements, and concurrency tables.

## Impact

A node with Kate RPC enabled can have its CPU exhausted by unauthenticated proof requests, degrading or interrupting light-client data availability sampling that the node serves. The attacker pays only the cost of HTTP requests and needs no account or tokens. The impact is confined to individual nodes and does not affect chain consensus. Current mainnet blocks are mostly small, so per-request cost is presently low, but the cost scales with block utilization, and the absence of any handler-level defense is a definite gap. Against an enabled node serving full 4 MB blocks the availability impact rises toward High under the vector `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`.

Affects the **Liveness** axis — unauthenticated KZG computation exhausts the node serving sampling — where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 5.3/10 (Medium)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Requests are sent over the public RPC endpoint |
| AC (Attack Complexity) | L (Low) | Standard JSON-RPC calls trigger the computation |
| PR (Privileges Required) | N (None) | No account or credentials required |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the targeted node |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | N (None) | No integrity impact |
| A (Availability) | L (Low) | CPU pressure degrades the node; rises to High on enabled nodes serving full blocks |

## Recommendation

1. Add per-IP rate limiting to the expensive Kate methods rather than relying on the global, per-connection Substrate limiter.
2. Cache the polynomial grid per block in an LRU so repeated cell proofs reuse a single grid construction.
3. Bound concurrent KZG computation with a semaphore so a burst of requests cannot saturate every core.
4. For nodes serving data availability sampling, require lightweight authentication and limit JSON-RPC batch sizes for Kate methods.
