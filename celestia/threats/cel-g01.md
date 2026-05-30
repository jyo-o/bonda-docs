# CEL-G01: KYC Validator Concentration Enabling Legal Censorship

{% hint style="warning" %}
**Severity**: High (8.7/10) · **STRIDE**: G · **Status**: verified
{% endhint %}

## Summary

Celestia's validator set is highly concentrated: only 8 validators are needed to exceed the one-third voting power threshold, and 6 of these 8 are KYC-regulated financial institutions under US, EU, Swiss, and Hong Kong jurisdictions. A single coordinated judicial action or sanctions designation targeting 6-7 KYC entities could compel sufficient voting power to perform indefinite transaction censorship via the prevote-nil mechanism, with no available on-chain countermeasure.

## Description

The root cause is a combination of validator set concentration, regulatory surface area, and the absence of any on-chain mechanism to detect or penalize censorship behavior.

**Voting Power Concentration**

Mainnet staking data (2026-05-24) shows that the top 8 validators hold 35.77% of voting power, exceeding the one-third threshold required for censorship via prevote-nil. The top 28 validators hold 67.02%, exceeding the two-thirds threshold. Anchorage Digital alone controls 11.08% of voting power.

**Validator Set Saturation**

The `max_validators` parameter is set to 100 with 94 currently bonded, effectively blocking new entrants. Out of 301 total registered validators, only 94 are bonded, 192 are unbonding, and 15 are in other states. This saturation prevents dilution of the concentrated power through new independent validators.

**Regulatory Attack Surface**

Six of the top 8 validators are KYC-regulated entities operating under jurisdictions with established legal mechanisms for compelling compliance. A court order or OFAC sanctions designation targeting these 6-7 entities would align more than one-third of voting power for censorship purposes.

**Censorship Mechanism**

When targeted blocks are proposed, compelled validators cast prevote-nil, preventing the block from reaching the two-thirds prevote threshold required for finalization. The protocol cannot distinguish between honest nil votes (e.g., proposal not received) and malicious censorship because there is no nil-vote evidence type in the evidence subsystem:

```go
// celestia-core/types/evidence.go:22-219
// Only DuplicateVoteEvidence and LightClientAttackEvidence are implemented
// No nil-vote evidence type exists
```

```go
// celestia-core/consensus/state.go:1553-1577
// Honest and malicious prevote-nil follow the same code path
```

The on-chain cost is zero. Mainnet slashing parameters (2026-05-20, height 11,172,730) confirmed via `celestia-rest.publicnode.com/cosmos/slashing/v1beta1/params`:
- `slash_fraction_downtime=0`
- `min_signed_per_window=0.001` (10 of 10,000 blocks)
- `downtime_jail_duration=60s`

Cartel members can avoid jail by signing as few as 10 out of 10,000 blocks (0.1%). PR `celestia-app#7090` (merged 2026-04-17) changed these defaults "to match mainnet governance." Only `slash_fraction_double_sign=0.02` carries any penalty, and prevote-nil is not classified as a double sign.

Because validators act under legal obligation, there is no economic deterrent or community remedy. Delegator diversification does not help because redistributing stake among the same validators does not reduce the number of entities needed to reach the threshold.

## Proof of Concept

No proof of concept was conducted for this threat. Evidence is based on on-chain staking data cross-verified across three independent endpoints (publicnode, polkachu, pops.one) as of 2026-05-24.

## Impact

Legally enforced, indefinite transaction censorship with zero technical cost and no available on-chain countermeasure. The attack leverages existing regulatory compliance obligations and cannot be addressed through slashing or social consensus mechanisms. The censorship can continue as long as the judicial order remains in effect, which could be indefinite.

### CVSS 3.1

**Score**: 8.7/10 (High)
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV (Attack Vector) | N (Network) | Censorship is executed via network-level prevote-nil messages |
| AC (Attack Complexity) | H (High) | Requires coordinated judicial action across multiple jurisdictions targeting 6-7 entities |
| PR (Privileges Required) | N (None) | No protocol-level privileges needed; attack is executed via legal compulsion of existing validators |
| UI (User Interaction) | N (None) | No user interaction required; validators comply with legal orders |
| S (Scope) | C (Changed) | Censorship affects all users and L2 rollups depending on Celestia DA, crossing trust boundaries |
| C (Confidentiality) | N (None) | No confidentiality impact |
| I (Integrity) | H (High) | Targeted transactions are permanently excluded from the canonical chain |
| A (Availability) | H (High) | Targeted namespaces or transaction types become permanently unavailable |

## Recommendation

1. Introduce a nil-vote evidence type in the evidence subsystem to enable detection of systematic nil-voting patterns.
2. Set `slash_fraction_downtime` above zero via governance to create at least minimal cost for nil-voting behavior.
3. Create incentive programs for non-KYC validator participation to reduce the regulatory attack surface across the top-8 set.
4. Increase `MaxValidators` beyond 100 to reduce validator set saturation and allow new independent validators to join.
5. Explore a correlation penalty mechanism that increases slashing for coordinated nil-voting by multiple validators.
6. Provide L2 and user-side censorship resistance SLA evaluation tools to enable downstream consumers to assess their exposure to this risk.
