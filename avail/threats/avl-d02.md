# AVL-D02: Low Validator Utilization Concentrates Consensus Power

{% hint style="info" %}
**Severity**: Medium (5.9/10) · **STRIDE**: D · **Status**: Verified
{% endhint %}

## Summary

Avail's mainnet supports up to 1,200 validator slots, but only 105 are currently active (8.75% utilization). The Nakamoto coefficient is approximately 34, meaning an attacker would need to compromise at least 34 validators to disrupt consensus. While the NPoS Phragmen election produces a very even stake distribution (1.20x max/min ratio), the small active set relative to capacity increases concentration risk.

## Description

The validator set operates at low utilization with 105 of 1,200 available slots filled. Total staked amount is approximately 4.794 billion AVAIL (~48% of 10 billion total supply).

```
// @audit — Validator set metrics (Era #688):
//          Active validators: 105 / 1,200 slots (8.75% utilization)
//          Nakamoto coefficient: ~34 (33.33% stake threshold)
//          Full BFT attack: 70 validators (66.67% stake)
//          Top validator: 50.79M AVAIL (1.06% of total stake)
//          Bottom validator: 42.4M AVAIL (0.88%)
//          Max/min stake ratio: 1.20x
//          Top 10 validators: 10.54% of total stake
```

The Phragmen election algorithm achieves remarkably even stake distribution, making it significantly harder for any small group to accumulate disproportionate influence. However, the small absolute number of active validators means fewer independent operators need to be compromised for a consensus attack.

## Proof of Concept

On-chain state and Subscan Era #688 data were analyzed. See [Verification Evidence](../evidence.md#6-avail-chain-verification) for full commands and results.

- `Session.Validators` storage query returns 105 active validators out of 1,200 slots
- Nakamoto coefficient of ~34 calculated from stake distribution; max/min stake ratio of 1.20x confirms Phragmen equalization
- Top validator holds 1.06% of total stake (50.79M AVAIL)

## Impact

An attacker controlling 34 or more validators (~33.33% of stake) could block finality by refusing to vote on blocks. With 70 or more compromised validators (~66.67% of stake), the attacker could seize full control of finality, potentially censoring transactions, reorganizing blocks, or halting the chain entirely. However, the even Phragmen distribution requires targeting many validators with similar stake levels rather than focusing on a few high-stake validators.

### CVSS 3.1
**Score**: 5.9/10 (Medium)  
**Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| AV | N (Network) | Attack operates at the network level through validator collusion |
| AC | H (High) | Requires coordinated collusion of 34+ validators with even stake distribution |
| PR | N (None) | Validator credentials can be obtained by anyone who stakes |
| UI | N (None) | No user interaction required |
| S | U (Unchanged) | Impact stays within the chain's finality scope |
| C | N (None) | No confidentiality impact |
| I | N (None) | No integrity impact from validator collusion alone |
| A | H (High) | Finality disruption is possible if the 33.33% threshold is reached |

## Recommendation

1. **Incentivize validator set growth**: Implement mechanisms to attract more validators toward the 1,200 slot capacity, increasing the Nakamoto coefficient and the practical cost of collusion.
2. **Monitor stake concentration metrics**: Continuously track the Nakamoto coefficient and flag any significant changes in validator set composition or stake distribution.
3. **Implement validator diversity requirements**: Consider geographic or organizational diversity requirements to reduce the risk of coordinated compromise across the validator set.
