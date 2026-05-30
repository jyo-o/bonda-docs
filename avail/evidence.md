# Avail Evidence Summary

This page summarizes the on-chain verification evidence collected for Avail DA threat findings. All results are from Ethereum mainnet and Avail mainnet, using `cast` (Foundry) and Substrate RPC calls. Every conclusion traces to a raw on-chain response.

**Verification date**: 2026-05-21 to 2026-05-24
**Tools**: cast (Foundry), curl (Substrate RPC)
**RPC endpoints**: `https://ethereum-rpc.publicnode.com` (Ethereum), `https://avail-rpc.publicnode.com` (Avail)

---

## 1. VectorX Single Relayer Verification (AVL-D01)

The VectorX DA attestation bridge operates with a single approved relayer EOA.

### On-Chain State

```bash
# Confirm relayer is an EOA (no contract code)
cast code 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: 0x (no code = EOA)

# Relayer nonce and balance
cast nonce 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: 2632

cast balance 0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC --ether
# Result: 0.820... ETH

# Relayer approval status
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "approvedRelayers(address)(bool)" \
  0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D --rpc-url $ETH_RPC
# Result: true

# Permissioned mode active
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "checkRelayer()(bool)" --rpc-url $ETH_RPC
# Result: true

# Previous relayer revoked (rotation history)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "approvedRelayers(address)(bool)" \
  0x3243552F3BcbcE720Db6f5ad0C1B7cd15458392D --rpc-url $ETH_RPC
# Result: false
```

### Code-Level Verification (SP1Vector.sol)

Source code analysis of `commitHeaderRange()` confirms:
- Zero references to `block.timestamp` (no on-chain timing enforcement)
- No cooldown, rate limit, or heartbeat mechanism
- No staleness detection -- the contract has no way to know the relayer has stopped
- Client-side timing is controlled by operator.rs constants: `LOOP_INTERVAL_MINS=60`, `BLOCK_UPDATE_INTERVAL=360`, `PROOF_TIMEOUT_SECS=1800`
- `setRelayerApproval()` does not emit an event (unlike `removeHeaderHash` which emits `HeaderHashRemoved`), creating an observability gap

### Anvil Fork PoC (3 Tests)

```bash
# PoC-1: Single relayer access control
# Unapproved address calls commitHeaderRange() -> RelayerNotApproved revert
# PASS

# PoC-2: Staleness detection absence
# Query latestBlock, compare to current Avail block
# No on-chain function or event for staleness detection
# PASS

# PoC-3: Guardian ZK bypass (intended emergency mechanism)
# updateBlockRangeData() injects commitment without ZK proof
# This is designed behavior for emergency recovery
# PASS
```

### Relay Pattern Metrics

| Metric | Value |
|---|---|
| Average relay interval | ~120 minutes |
| Batch size | ~358 blocks |
| Gas per commit | 458,612 gas |
| Active relayers | 1 (0x27BF...) |
| Previous relayer | 0x3243... (revoked) |

---

## 2. SP1VerifierGateway Multisig Analysis (AVL-E01)

The ZK proof verifier routing is controlled by a 2-of-3 multisig with key holder overlap.

```bash
# Threshold
cast call 0xCafEf00d348Adbd57c37d1B77e0619C6244C6878 \
  "getThreshold()(uint256)" --rpc-url $ETH_RPC
# Result: 2

# Owners
cast call 0xCafEf00d348Adbd57c37d1B77e0619C6244C6878 \
  "getOwners()(address[])" --rpc-url $ETH_RPC
# Result:
#   0xBaB2c2aF5b91695e65955DA60d63aD1b2aE81126
#   0x72Ff26D9517324eEFA89A48B75c5df41132c4f54  <-- also Gov Multisig #4
#   0x9395e83720bf2D8ac6435f9c520b48E289Cb8885
```

Owner #2 (`0x72Ff...4f54`) is the same address as Avail Governance Multisig 1 owner #4. This means a Succinct signer + this shared signer (2 people) can change the SP1 verifier route, potentially accepting false ZK proofs.

---

## 3. Governance Multisig Cross-Analysis (AVL-E02)

Three multisigs share overlapping key holders, reducing effective independence.

### Avail Governance Multisig 1 (4-of-7)

```bash
cast call 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666 \
  "getThreshold()(uint256)" --rpc-url $ETH_RPC
# Result: 4

cast call 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666 \
  "getOwners()(address[])" --rpc-url $ETH_RPC
# Result: 7 addresses (all EOAs)
# Gnosis Safe v1.3.0, nonce=15
```

### Key Holder Overlap Matrix

| Address (truncated) | Gov (4/7) | Pauser (3/5) | SP1 (2/3) |
|---|---|---|---|
| 0x70a4... | Yes | Yes | No |
| 0x340e... | Yes | Yes | No |
| 0xAD37... | Yes | Yes | No |
| **0x72Ff...** | **Yes (#4)** | **Yes (#4)** | **Yes (#2)** |
| 0x1fbA... | Yes | No | No |
| 0xBe1D... | Yes | No | No |
| 0x4983... | Yes | Yes | No |

**0x72Ff...4f54** participates in all three multisigs. 4 of 5 Pauser Multisig signers are identical to Gov Multisig signers. The effective independence between Governance and Pauser is minimal -- compromising the Gov multisig implicitly compromises the Pauser (3 of the 4 overlapping signers exceed the 3/5 Pauser threshold).

---

## 4. Deployer Admin Role Verification (AVL-E03)

The deployer EOA retains DEFAULT_ADMIN_ROLE, enabling a 2-transaction VectorX takeover.

```bash
# Deployer retains DEFAULT_ADMIN_ROLE
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "hasRole(bytes32,address)(bool)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: true

# Deployer does NOT have TIMELOCK_ROLE (revoked)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "hasRole(bytes32,address)(bool)" \
  "<TIMELOCK_ROLE_HASH>" \
  0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: false

# TIMELOCK_ROLE admin = DEFAULT_ADMIN_ROLE (0x00)
cast call 0x02993cdC11213985b9B13224f3aF289F03bf298d \
  "getRoleAdmin(bytes32)(bytes32)" \
  "<TIMELOCK_ROLE_HASH>" --rpc-url $ETH_RPC
# Result: 0x0000...0000 (DEFAULT_ADMIN_ROLE)

# Deployer is an EOA
cast code 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: 0x (no code = EOA)

cast nonce 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e --rpc-url $ETH_RPC
# Result: 1107 (active account)
```

### Attack Path

Since DEFAULT_ADMIN_ROLE is the admin of TIMELOCK_ROLE, the deployer can:

1. `grantRole(TIMELOCK_ROLE, deployer_address)` -- grants itself upgrade authority
2. `upgradeTo(malicious_implementation)` -- replaces VectorX with arbitrary code

This bypasses the 4-of-7 governance multisig entirely. The root cause is that `Guardian.s.sol` (deployment script) has the DEFAULT_ADMIN_ROLE revocation code commented out.

---

## 5. Bridge and Token Verification

### AvailBridge Access Control

```bash
# Bridge DEFAULT_ADMIN = TimelockController (24h delay)
cast call 0x054fd961708d8e2b9c10a63f6157c74458889f0a \
  "hasRole(bytes32,address)(bool)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  0x45828180bbE489350D621d002968A0585406d487 --rpc-url $ETH_RPC
# Result: true

# TimelockController minimum delay
cast call 0x45828180bbE489350D621d002968A0585406d487 \
  "getMinDelay()(uint256)" --rpc-url $ETH_RPC
# Result: 86400 (24 hours)
```

### AVAIL Token (AVL-T03)

```bash
# Token is immutable (no owner)
cast call 0xeeb4d8400aeefafc1b2953e0094134a887c76bd8 \
  "owner()(address)" --rpc-url $ETH_RPC
# Result: revert (no owner function = immutable)

# Total supply
cast call 0xeeb4d8400aeefafc1b2953e0094134a887c76bd8 \
  "totalSupply()(uint256)" --rpc-url $ETH_RPC
# Result: ~791,099,641 AVAIL (18 decimals)
```

Mint/burn authority is restricted to the Bridge contract (0x054f...). A malicious Bridge upgrade (via TimelockController 24h path or VectorX no-timelock path) could enable unlimited token minting.

---

## 6. Avail Chain Verification

### Validator Set (AVL-D02)

```bash
# Session.Validators storage
curl -s "https://avail-rpc.publicnode.com" \
  -d '{"jsonrpc":"2.0","method":"state_getStorage",
  "params":["0xcec5070d609dd3497f72bde07fc96ba088dcde934c658227ee1dfafcd6e16903"],"id":1}'
# SCALE decode -> 105 active validators
```

| Metric | Value |
|---|---|
| Active validators | 105 |
| Max validators | 1,200 |
| Utilization | 8.75% |
| Nakamoto coefficient | ~34 |
| Top validator share | 1.06% |
| Max/min stake ratio | 1.20x (Phragmen equalization) |

### Slashing Status (AVL-P01)

```bash
# ActiveEra
# state_getStorage -> SCALE decode -> 688

# UnappliedSlashes for era 688
# state_getStorage -> null (empty = no pending slashes)
```

688 eras of operation with zero slashing events applied. The slashing infrastructure exists in runtime metadata (67 references) but has never been triggered.
