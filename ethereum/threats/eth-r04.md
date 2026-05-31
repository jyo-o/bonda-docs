# ETH-R04: c-kzg-4844 Go Binding Thread Safety

{% hint style="info" %}
**Severity**: Defense-in-Depth (no CVSS) · **STRIDE**: T (Tampering) · **Status**: code\_review
{% endhint %}

## Summary

The c-kzg Go binding uses package-level globals (`settings` and `loaded`) that are read and written **without any synchronization primitives**. Concurrent calls to `LoadTrustedSetup`/verify/`FreeTrustedSetup` can theoretically cause (1) C function calls with half-initialized `settings` (undefined behavior), (2) double initialization, and (3) use-after-free during concurrent Free and verify operations. `go test -race` reports data races on these accesses. In practice, standard usage loads the setup once from a single goroutine at startup, making real-world triggering unlikely. This is a **formal Go memory model violation / robustness defect**, not a remotely exploitable vulnerability.

## Description

### Vulnerable Code

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

func VerifyKZGProof(/* ... */) (bool, error) {
    if !loaded { return false, errors.New("not loaded") } // @audit unsynchronized read
    // @audit passes settings to C function -- concurrent Load/Free causes partial read / UAF
}

func FreeTrustedSetup() {
    if !loaded { return } // @audit unsynchronized read
    C.free_trusted_setup(&settings) // @audit Free while another goroutine verifies -- UAF
    loaded = false
}
```

### Race Scenarios

| Scenario | Goroutine A | Goroutine B | Result |
|----------|-------------|-------------|--------|
| #1 | `LoadTrustedSetup` (in progress) | `VerifyKZGProof` | C call with half-filled `settings` -- **undefined behavior** |
| #2 | `LoadTrustedSetup` | `LoadTrustedSetup` | Both pass `if loaded` check -- **double initialization** |
| #3 | `FreeTrustedSetup` (in progress) | `VerifyKZGProof` | Freed `settings` pointer used -- **use-after-free** |

### Root Cause

Reads and writes to `loaded` and `settings` violate the **Go memory model** (concurrent access without synchronization primitives). The API exposes multiple public functions without enforcing a no-concurrent-use contract through **documentation or types**.

### Critical Limitation

c-kzg documents its interface as **"single-threaded for simplicity"** and loading as **"run once at initialization."** The maintainer may respond that concurrent usage is "by design, out of scope." The persuasion point should focus on the **API contract gap** rather than the race itself.

### STRIDE Detail

| Category | Relevance | Analysis |
|----------|-----------|----------|
| **T -- Tampering** | **Primary** | C calls with half-initialized/freed `settings` corrupt KZG verification results (UB) / use-after-free causes memory corruption |
| D -- DoS | Indirect | UB/UAF may crash the node, causing denial of service (secondary effect of tampering) |

## Proof of Concept

No exploit reproduction was conducted. If performed, `go test -race` on the `bindings/go/` package would report data races on `settings`/`loaded` accesses.

**Recommended test (if conducted):**

```go
// race_test.go
func TestConcurrentLoadAndVerify(t *testing.T) {
    go func() {
        _ = LoadTrustedSetup(/* ... */)
    }()
    go func() {
        _, _ = VerifyKZGProof(/* ... */)
    }()
    // go test -race -> data race reported
}

func TestConcurrentFreeAndVerify(t *testing.T) {
    _ = LoadTrustedSetup(/* ... */)
    go func() {
        FreeTrustedSetup()
    }()
    go func() {
        _, _ = VerifyKZGProof(/* ... */)
    }()
    // go test -race -> data race reported (UAF scenario)
}
```

## Impact

1. Non-standard usage (concurrent Load/verify/Free) triggers data races
2. **Scenario #1:** C call with half-initialized `settings` -- **undefined behavior** leading to incorrect verification results
3. **Scenario #3:** Use-after-free -- **memory corruption** or **node crash**
4. **Cascade (theoretical):** Incorrect KZG verification results could accept invalid proofs or reject valid ones

No CVSS score is assigned. There is no remote reachability, and the issue does not manifest under standard usage. This is classified as a **robustness / API contract** improvement.

## Recommendation

### Patch -- Protect with `sync.RWMutex`

> `sync.Once` + `atomic.Bool` does not prevent Scenario #3 (UAF) -- a TOCTOU window remains between the `loaded` check and the C call. `sync.Once` also prevents free-and-reload.

```go
// [Before]
var loaded   = false
var settings = C.KZGSettings{}

// [After]
var (
    settings C.KZGSettings
    loaded   bool
    mu       sync.RWMutex
)

func LoadTrustedSetup(/* ... */) error {
    mu.Lock(); defer mu.Unlock()
    if loaded { return errors.New("trusted setup is already loaded") }
    if ret := C.load_trusted_setup(&settings /* ... */); ret != C.C_KZG_OK {
        return makeErrorFromRet(ret)
    }
    loaded = true
    return nil
}

func FreeTrustedSetup() {
    mu.Lock(); defer mu.Unlock()
    if !loaded { return }
    C.free_trusted_setup(&settings)
    loaded = false
}

func VerifyKZGProof(/* ... */) (bool, error) {
    mu.RLock(); defer mu.RUnlock()   // @audit RLock held until C call completes -- prevents UAF
    if !loaded { return false, errors.New("trusted setup is not loaded") }
    // ... all C calls using &settings within RLock ...
}
// @audit apply same RLock pattern to remaining 12 verify/compute functions
```

**Performance note:** `RLock` costs a single atomic add when uncontended, negligible compared to KZG pairing operations (several ms).

**Alternative:** Remove `FreeTrustedSetup` from the concurrent-safety contract and explicitly document it as **"concurrent-unsafe"**.
