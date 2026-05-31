# ETH-R04: c-kzg-4844 Go Binding Thread Safety

{% hint style="info" %}
**Severity**: Low (3.4/10) · **STRIDE**: R · **Status**: code\_review
{% endhint %}

## Summary

The c-kzg Go binding uses package-level globals (`settings` and `loaded`) that are read and written without any synchronization primitives. Concurrent calls to `LoadTrustedSetup`/verify/`FreeTrustedSetup` can theoretically cause C function calls with half-initialized `settings`, double initialization, and use-after-free. In practice, standard usage loads the setup once from a single goroutine at startup, making real-world triggering unlikely. This is a formal Go memory model violation, not a remotely exploitable vulnerability.

## Description

The Go binding exposes 13 public functions that reference global mutable state without synchronization:

```go
// bindings/go/main.go
// https://github.com/ethereum/c-kzg-4844
var loaded   = false           // @audit no sync.Once / atomic / mutex
var settings = C.KZGSettings{} // @audit global mutable state, referenced by 13 functions without synchronization

func LoadTrustedSetup(/* ... */) error {
    if loaded { return errors.New("already loaded") } // @audit unsynchronized read -- race
    // ... C.load_trusted_setup(&settings, ...) ...
    loaded = true // @audit unsynchronized write -- race
    return nil
}

func FreeTrustedSetup() {
    if !loaded { return } // @audit unsynchronized read
    C.free_trusted_setup(&settings) // @audit Free while another goroutine verifies -- UAF
    loaded = false
}
```

Three race scenarios exist: concurrent Load and verify causes C calls with half-filled `settings`; concurrent Load and Load causes double initialization; concurrent Free and verify causes use-after-free. c-kzg documents its interface as single-threaded for simplicity, so the maintainer may consider concurrent usage out of scope. The core issue is the API contract gap rather than the race itself.

## Proof of Concept

No exploit reproduction was conducted. If performed, `go test -race` on the `bindings/go/` package would report data races on `settings`/`loaded` accesses.

## Impact

Non-standard concurrent usage triggers data races that can cause undefined behavior, memory corruption, or node crashes. Incorrect KZG verification results could accept invalid proofs or reject valid ones.

### CVSS 3.1

**Score**: 3.4/10 (Low)
**Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | L (Local) | Exploiting client divergence requires local access to a specific client implementation's processing pipeline |
| AC (Attack Complexity) | H (High) | Requires identifying a parsing divergence across multiple client implementations and crafting input that triggers differential behavior |
| PR (Privileges Required) | L (Low) | Requires ability to submit blobs as a regular network participant |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to nodes running the specific client implementation with the divergent behavior |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | Client divergence may cause inconsistent DA attestations across implementations, but multi-client redundancy limits systemic impact |
| A (Availability) | L (Low) | Affected client instances may temporarily reject valid data or accept invalid data, causing partial availability degradation |

## Recommendation

1. Protect `settings` and `loaded` with `sync.RWMutex`: `Lock` for Load/Free, `RLock` for all 13 verify/compute functions.
2. `sync.Once` + `atomic.Bool` is insufficient because a TOCTOU window remains between the `loaded` check and the C call, failing to prevent the use-after-free scenario.
3. Alternatively, remove `FreeTrustedSetup` from the concurrent-safety contract and explicitly document it as concurrent-unsafe.
