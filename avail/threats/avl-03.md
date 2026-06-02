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

Cost-scaling and cache-absence behavior were measured against a local development network and the public mainnet RPC. Measurements were taken under ARM64 emulation, so absolute timings are indicative of scaling rather than native throughput.

- **No server-side caching**: repeated `kate_queryProof` calls against the same mainnet block returned near-identical cold and warm timings, confirming the grid is rebuilt each time.
- **Cost scales with block size**: per-request time for a single cell rose from about 5 ms at 1 KB to about 96 ms at 1 MB on the local network.
- **Concurrency saturation**: 50 concurrent requests against a 1 MB block raised wall-clock time to roughly 8.4 times the sequential baseline, indicating CPU saturation.
- **Mainnet exposure**: `kate_queryProof` returned a valid KZG proof from `mainnet-rpc.avail.so` with no authentication.

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
