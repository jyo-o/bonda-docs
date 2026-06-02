# EDA-06: Dead Operators Serving Zero Chunks Despite Active BLS Signing

{% hint style="info" %}
**Severity**: Medium · **Category**: Operational Risk · **Status**: verified
{% endhint %}

## Summary

A 24-hour prober measurement of 79 EigenDA operators revealed that 11 operators (13.9%) are completely dead. These operators return a 0% success rate on chunk retrieval via `GetChunks`, yet continue to sign BLS attestations.

The root cause is the absence of a slashing mechanism (EDA-11) that would economically penalize non-serving behavior. These operators are free-riding candidates: collecting rewards from BLS attestation signing without fulfilling data availability obligations.

The current 13.9% non-response rate remains below the Reed-Solomon erasure coding reconstruction threshold of 22%, but further degradation would erode this safety margin.

## Description

![EDA-06 data flow — EigenDA Dispersal path](https://raw.githubusercontent.com/jyo-o/bonda-docs/main/eigenda/assets/dfd/eigenda-dispersal.png)

*Data flow — EigenDA Dispersal: Operators.*

Prober measurement results across 79 operators:

- 11 operators: completely dead (0.0% success rate)
- 2 operators: degraded (less than 90% success)
- 66 operators: healthy
- Dead operators include recognizable entities: chorus.one, swell-eigenda, attestant.io

The signing-info comparison reveals a gap between attestation activity and actual data serving. The 1h/24h signing-info shows only 3 dead operators, while the prober detected 11 non-responsive operators. This creates an 8-operator gap between signing activity and chunk serving, consistent with the free-rider hypothesis. These operators sign BLS attestations to appear active but do not store or serve data chunks.

This finding is directly connected to EDA-11. Without economic penalties from slashing, there is no disincentive for this behavior. As more operators adopt this strategy, the dead operator count could grow to exceed the 22% Reed-Solomon reconstruction threshold.

## Proof of Concept

A 24-hour prober measurement was conducted across 79 operators. See [Verification Evidence](../evidence.md#dead-operator-measurement-eda-06) for full data.

- Prober detected 11 dead operators (0.0% chunk-serving success rate)
- DataAPI signing-info shows only 3 dead operators, revealing an 8-operator gap
- The gap indicates operators signing BLS attestations without serving data chunks

## Impact

11 out of 79 operators (13.9%) are non-responsive to chunk retrieval requests while continuing to sign BLS attestations. This degrades data availability quality and creates free-riding incentives for other operators.

The current rate is below the 22% Reed-Solomon erasure coding threshold, so the system operates within its fault tolerance bounds. However, without slashing (EDA-11), the dead operator count may continue to increase. If it exceeds 22%, data recovery becomes unreliable and the fundamental DA guarantee is weakened.

No special privileges or authentication are needed to free-ride. Any registered operator can adopt this behavior.

Affects the Retrievability axis. It is tracked as an Operational Indicator shown alongside the risk pentagon, not as a deduction from the structural score.

## Recommendation

1. Implement slashing for non-serving operators to create economic disincentives for free-riding (related to EDA-11).
2. Establish automated monitoring and alerting for operator chunk-serving health to enable faster detection of dead operators.
3. Use the existing ejection mechanism (EDA-08) to remove confirmed dead operators from the quorum.
4. Consider implementing proof-of-custody or periodic data availability challenges to detect free-riding before it accumulates.
