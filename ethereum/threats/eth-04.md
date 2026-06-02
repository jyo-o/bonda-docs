# ETH-04: c-kzg-4844 Go Binding Thread Safety

{% hint style="info" %}
**Severity**: Low (3.4/10) · **Likelihood**: Low · **Category**: Vulnerability · **Status**: verified
{% endhint %}

## Summary

The c-kzg Go binding uses package-level globals (`settings` and `loaded`) that are read and written without any synchronization primitives. Concurrent calls to `LoadTrustedSetup`/verify/`FreeTrustedSetup` can theoretically cause C function calls with half-initialized `settings`, double initialization, and use-after-free. In practice, standard usage loads the setup once from a single goroutine at startup, making real-world triggering unlikely. This is a formal Go memory model violation, not a remotely exploitable vulnerability.

## Description

![ETH-04 data flow — Ethereum PeerDAS Read path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/ethereum/assets/dfd/ethereum-read.png)

*Data flow — Ethereum PeerDAS Read: DA Checker.*

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

Affects the **Verifiability** axis — unsynchronized state can yield incorrect KZG verification results — where it produces a Layer 3 deduction while unpatched.

### CVSS 3.1

**Score**: 3.4/10 (Low)
**Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | L (Local) | The race is on package-level globals inside the process; triggering it requires running code in the same process as the binding, with no network-reachable trigger |
| AC (Attack Complexity) | H (High) | Requires non-standard concurrent calls to `LoadTrustedSetup`/verify/`FreeTrustedSetup` that interleave on the unsynchronized globals — a window standard single-goroutine startup never opens |
| PR (Privileges Required) | L (Low) | Requires the ability to invoke the binding's functions concurrently from within the host process |
| UI (User Interaction) | N (None) | No user interaction required |
| S (Scope) | U (Unchanged) | Impact is confined to the process that loaded the binding |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | L (Low) | A race on `settings` can yield incorrect KZG verification results, accepting invalid or rejecting valid proofs |
| A (Availability) | L (Low) | A use-after-free or half-initialized `settings` can crash the node |

## Recommendation

1. Protect `settings` and `loaded` with `sync.RWMutex`: `Lock` for Load/Free, `RLock` for all 13 verify/compute functions.
2. `sync.Once` + `atomic.Bool` is insufficient because a TOCTOU window remains between the `loaded` check and the C call, failing to prevent the use-after-free scenario.
3. Alternatively, remove `FreeTrustedSetup` from the concurrent-safety contract and explicitly document it as concurrent-unsafe.
