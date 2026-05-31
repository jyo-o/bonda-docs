# ETH-R04: c-kzg-4844 Go Binding Thread Safety

{% hint style="info" %}
**Severity**: Defense-in-Depth (no CVSS) · **STRIDE**: T (Tampering) · **Status**: code\_review
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

No CVSS score is assigned. There is no remote reachability, and the issue does not manifest under standard usage. This is classified as a robustness / API contract improvement.

## Recommendation

1. Protect `settings` and `loaded` with `sync.RWMutex`: `Lock` for Load/Free, `RLock` for all 13 verify/compute functions.
2. `sync.Once` + `atomic.Bool` is insufficient because a TOCTOU window remains between the `loaded` check and the C call, failing to prevent the use-after-free scenario.
3. Alternatively, remove `FreeTrustedSetup` from the concurrent-safety contract and explicitly document it as concurrent-unsafe.
