#!/usr/bin/env python3
"""Generate GitBook markdown pages from threat JSON data.

Reads EigenDA and Avail threat JSON files, translates Korean fields to English,
and writes individual markdown pages to the bonda-docs output directories.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Korean -> English translation map (manual, domain-specific)
# ---------------------------------------------------------------------------

KO_EN = {
    # Common phrases
    "부재": "Absence",
    "미구성": "Misconfiguration",
    "위협": "Threat",
    "검증": "Verification",
    "없음": "None",
    "미적용": "Not Applied",
    "미검증": "Unverified",
    "미입증": "Unproven",
    "미완성": "Incomplete",
    "미발동": "Not Triggered",
    "잔류": "Residual",
    "탈취": "Compromise",
    "우회": "Bypass",
    "장악": "Takeover",
    "담합": "Collusion",
    "기만": "Deceptive",
    "비대칭": "Asymmetric",
    "집중": "Concentration",
}


# ---------------------------------------------------------------------------
# STRIDE category from SID prefix
# ---------------------------------------------------------------------------

def stride_from_sid(sid: str) -> str:
    """Extract STRIDE category letter from SID."""
    # SID format: XXX-Y## where Y is STRIDE letter
    # EDA-D02 -> D (Denial of Service)
    # AVL-E03 -> E (Elevation of Privilege)
    # G-CON-03 -> special case
    parts = sid.split("-")
    if len(parts) == 3 and parts[0] == "G":
        # G-CON-03 type
        cat = parts[1][0] if parts[1] else "?"
        stride_map = {
            "C": "Concentration (Infra)",
        }
        return stride_map.get(cat, cat)
    elif len(parts) == 2:
        cat = parts[1][0]
    else:
        cat = "?"
    stride_map = {
        "S": "Spoofing",
        "T": "Tampering",
        "R": "Repudiation",
        "I": "Information Disclosure",
        "D": "Denial of Service",
        "E": "Elevation of Privilege",
        "P": "Protocol Design",
    }
    return stride_map.get(cat, cat)


def stride_letter(sid: str) -> str:
    """Get just the STRIDE letter for display."""
    parts = sid.split("-")
    if len(parts) == 3 and parts[0] == "G":
        return parts[1][:3]
    elif len(parts) == 2:
        return parts[1][0]
    return "?"


# ---------------------------------------------------------------------------
# Korean to English translation (manual per-field)
# ---------------------------------------------------------------------------

# Since we can't use an API for translation, we'll do a best-effort approach:
# translate each threat's Korean text fields programmatically.
# The Korean text is technical and domain-specific, so we provide
# hand-crafted translations keyed by SID.

TRANSLATIONS = {
    # ---- EigenDA ----
    "EDA-D02": {
        "title": "Proxy HTTP Server Rate Limit Absence",
        "details": "The Proxy REST server lacks rate limiter middleware. ReadHeaderTimeout is 10s, WriteTimeout is 40min. Body size is limited to MaxServerPOSTRequestBodySize=16MB, but there is no request count limit. Default bind is 0.0.0.0, however code comments (routing.go) and README explicitly state 'not intended for external exposure / NEVER publicly accessible' -- it is designed as a private sidecar. External exposure only occurs when operators fail to configure firewalls, and impact is limited to that specific rollup operator. No protocol-level impact.",
        "prerequisites": "Proxy exposed to the internet without firewall (operator misconfiguration)",
        "mitigations": "http.MaxBytesReader limits body size, but no request count limit exists. If the operator configures firewall/reverse-proxy access controls, the attack surface is eliminated.",
        "condition": "target.controls.handlesResourceConsumption is False and target.port != 0",
        "example": "",
        "verification_note": "PoC #08 confirmed only global throttle; Proxy (EigenDA client-side) is separate. PoC #09: cross-check OK. External exposure is unintended by design (downgraded to AC:H).",
        "bvss_rationale": "B:N -- No direct financial impact. AV:N -- Network exposure when firewall is not applied. AC:H -- Designed as a private sidecar; external exposure only occurs with operator misconfiguration (explicitly stated in code and documentation). A:L/AI:L -- Impact limited to the specific rollup sidecar; no protocol-level effect.",
    },
    "EDA-S03": {
        "title": "Cross-chain Signature Replay (anchor_signature Not Enforced)",
        "details": "TolerateMissingAnchorSignature is a cli.BoolTFlag (default TRUE). The mainnet disperser accepts dispersal without anchor_signature. The anchor_signature mechanism was introduced after Sigma Prime EDA2-02, 11, 18 fixes, but remains non-enforced with default true. DisableAnchorSignatureVerification is a cli.BoolFlag (default false). At the proto level, disperser_v2.proto DisperseBlobRequest.anchor_signature is field 5 (implicit-optional), so the proto definition itself permits omission. No anchor-related errors appear in proxy operation logs. [Consolidated with EDA-T12] The ability to omit anchor_signature is redundantly permitted at two layers: proto design (optional field) and server flag (BoolTFlag=true).",
        "prerequisites": "Ability to send dispersal requests without anchor_signature",
        "mitigations": "The anchor_signature mechanism exists but is non-enforced with default true. TODO: set to false and remove.",
        "condition": "",
        "example": "",
        "verification_note": "Code confirms default TolerateMissingAnchorSignature=true. Live test (2026-05-24): ephemeral wallet DisperseBlob without anchor_signature -> gRPC Internal(no reservation found) -- not an anchor error -- confirms TolerateMissingAnchorSignature=true in production.",
        "bvss_rationale": "B:N -- No direct financial loss path proven. AC:H -- ECDSA signature required + mechanism itself exists (just non-enforced by default). PR:R -- Valid signature required. S:C -- Cross-chain replay possible. I:M/II:M -- Anchor non-enforced but onchain BLS verification remains.",
    },
    "EDA-D03": {
        "title": "Disperser V2 KZG Compute Surface Exposed Without Auth/Prepayment",
        "details": "The core issue is two specific surfaces that actually burn KZG compute, not V2 gRPC in general. GetBlobCommitment calls committer.GetCommitmentsForPaddedLength directly without auth/payment, and its disable flag defaults to false, making it exposed by default. A mainnet single read probe confirmed an actual BlobCommitmentReply response. DisperseBlob also recomputes KZG commitment in validateDispersalRequest before calling AuthorizePayment, so a well-formed request with valid blob/header/signature consumes CPU before reservation/payment rejection. In contrast, GetBlobStatus bursts are DynamoDB read paths and are not directly relevant to this threat.",
        "prerequisites": "Access to Disperser gRPC endpoint. The DisperseBlob path requires constructing valid blob/header/signature.",
        "mitigations": "Payment is only enforced after DisperseBlob processing, not on GetBlobCommitment. Cloudflare/WAF may exist upstream but app-layer thresholds are unverified.",
        "condition": "",
        "example": "",
        "verification_note": "PoC #02's 100 parallel GetBlobStatus is a cheap read path and inadequate as direct evidence. Instead, mainnet read-only probe confirmed reflection + GetBlobCommitment live response. Local exact-path reproduction showed baseline 1.77s -> C=8 p50 15.29s. Large-scale mainnet exploitability remains unverified due to Cloudflare/WAF.",
        "bvss_rationale": "B:N -- No financial impact; computing resource exhaustion. AV:N -- Public gRPC. AC:H -- Mainnet WAF/CDN protection layer presumed (unverified); impact confirmed only in local PoC, production-scale exploitability uncertain. A:H -- Unauthenticated KZG compute surface exposure confirmed. AI:M -- Actual service disruption level at production infrastructure scale unproven; auto-scaling/replica possible.",
    },
    "EDA-E01": {
        "title": "DisableAnchorSignatureVerification Flag Bypasses All Anchor Verification",
        "details": "DisableAnchorSignatureVerification is a cli.BoolFlag (default false). TolerateMissingAnchorSignature is a cli.BoolTFlag (default true). No anchor-related errors/warnings appear in mainnet proxy logs -- it is presumed that anchor verification is currently being skipped or operating in tolerate mode, though the disperser-side configuration cannot be directly verified.",
        "prerequisites": "Server configuration change permission or ability to inject environment variables",
        "mitigations": "Default is false. TODO: temporary flag, will be removed.",
        "condition": "",
        "example": "",
        "verification_note": "Code confirms default DisableAnchorSignatureVerification=false. Mainnet disperser settings cannot be directly verified -- code path only.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- Requires server environment variable access. AC:H -- Default false, intentional activation required. PR:R -- Server administrator privileges. I:H/II:M -- Anchor verification bypass, but other verification layers like BLS verification remain.",
    },
    "EDA-D04": {
        "title": "Encoding Failure Transitions Blob to Failed (No Fallback Path)",
        "details": "After 3 retries with exponential backoff (2^i seconds), encoder failure transitions blob to Failed state. No alternative encoding path exists. Probe measurements found 32 Failed blobs out of 491,479 total. All were from the same account (0x41fa...) during mass dispersal.",
        "prerequisites": "Encoder failure or overload",
        "mitigations": "3 retries + exponential backoff.",
        "condition": "",
        "example": "",
        "verification_note": "8307 blob sample showed 0.024% Failed (2 blobs). Corrected to 4 attempts (initial + 3 retries).",
        "bvss_rationale": "B:N -- No financial impact. AC:H -- Only occurs under encoder overload conditions; measured at 0.024%. PR:R -- Dispersal permission required. A:L/AI:L -- 3 retries + exponential backoff exist; limited to individual blob failures.",
    },
    "EDA-I02": {
        "title": "BLS Private Key Exposure on Node Process Compromise",
        "details": "The Node process holds BLS private keys in memory. If the process is compromised, the corresponding operator's signatures can be forged. Probe measurements detected evidence of some IPs having downed Node processes (GetChunks connection refused).",
        "prerequisites": "Node process compromise",
        "mitigations": "Process security (OS-level).",
        "condition": "",
        "example": "",
        "verification_note": "BLS keypair storage method is an operational domain concern; external verification not possible. PoC #09: cross-check OK.",
        "bvss_rationale": "B:N -- Protocol-level fund theft path unproven (single operator signature forgery). AV:P -- Requires Node process compromise (OS level). AC:H -- Requires OS security breach. C:H/CI:H -- BLS private key exposure. I:H/II:M -- Can forge signatures for the compromised operator but limited to single operator.",
    },
    "EDA-D06": {
        "title": "Relay Single Point of Failure (1 Relay on Mainnet)",
        "details": "RelayRegistry (0xD160e6...) onchain query shows nextRelayKey=1. Only key 0 is registered: address=0xe8437B..., url=relay-0-mainnet-ethereum.eigenda.xyz. Keys 1-5 are all 0x0 (unregistered). Only onlyOwner can add relays; no deletion function exists.",
        "prerequisites": "Relay failure",
        "mitigations": "Validator fallback (GetChunks) exists but only activates after relay failure.",
        "condition": "",
        "example": "",
        "verification_note": "Mainnet has 1 relay (nextRelayKey=1).",
        "bvss_rationale": "B:N -- No direct financial impact. AV:N -- Public endpoint. AC:L -- Only 1 mainnet relay (nextRelayKey=1 confirmed onchain); any failure immediately impacts read path. A:H -- Primary read path SPOF. AI:M -- GetChunks fallback exists so not complete outage but degraded performance; validator direct retrieval possible (auto-switches after relay failure).",
    },
    "EDA-D07": {
        "title": "GetBlob Unauthenticated -- Relies Solely on Rate Limiting",
        "details": "Relay's GetBlob has no authentication, and the rate limiter has no per-client field -- only global limits. Mainnet testing showed GetBlob accepts unauthenticated access (NotFound response), and 31 instances of 429 Too Many Requests were observed over 7 days, demonstrating global rate limit exhaustion. In contrast, GetChunks requires operator authentication (returns InvalidArgument), showing asymmetric auth policies between GetBlob and GetChunks.",
        "prerequisites": "Access to Relay endpoint",
        "mitigations": "Rate limit exists.",
        "condition": "",
        "example": "",
        "verification_note": "grpcurl without auth headers achieved 50/50 retrieval success.",
        "bvss_rationale": "B:N -- No financial impact. AV:N -- Unauthenticated access. AC:L -- Confirmed on mainnet. A:L/AI:M -- Read-only path, but legitimate users also receive 429 when global rate limit is reached (31 instances observed over 7 days).",
    },
    "EDA-E02": {
        "title": "Single 3-of-4 Multisig Controls 8 Core Contracts Simultaneously",
        "details": "Gnosis Safe 0x002721... (3-of-4 multisig, no timelock) is the owner of 8 core contracts: ServiceManager (0x870679...), RegistryCoordinator (0x0BAAc7...), EjectionManager (0x130d8E...), ThresholdRegistry (0xdb4c89...), RelayRegistry (0xD160e6...), DisperserRegistry (0x78cb05...), PaymentVault (0xb2e7ef...), CertVerifierRouter (0x1be725...). All 4 signers are EOAs (0xA3e302..., 0x1b6cC4..., 0x403F4d..., 0x891bbC...) with no ENS or metadataURI set, making onchain identity verification impossible. Compromising 3 keys enables total governance takeover. Impact scenarios: (1) ThresholdRegistry -- modify confirmationThreshold/adversaryThreshold to manipulate security inequality. (2) CertVerifierRouter -- addCertVerifier() to replace cert verification logic. CertVerifier itself (0x61692e...) is immutable (owner() reverts) but can be bypassed via Router. (3) PaymentVault -- withdraw(uint256) onlyOwner to drain vault balance. (4) EjectionManager -- force eject operators to manipulate quorum. (5) DisperserRegistry/RelayRegistry -- replace disperser/relay to control data paths.",
        "prerequisites": "Compromise 3 of 4 signer private keys. Signers: 0xA3e302..., 0x1b6cC4..., 0x403F4d..., 0x891bbC...",
        "mitigations": "3-of-4 multisig structure. Also noted by Dedaub N1. However, signer identities are not onchain-verified.",
        "condition": "",
        "example": "",
        "verification_note": "DA Ops Safe 3-of-4, all EOAs, no timelock. 17 contracts of which 12 are EIP-1967 proxies under a single ProxyAdmin. CertVerifier confirmed immutable; Router-based replacement confirmed possible.",
        "bvss_rationale": "B:N -- Multisig key compromise leading to fund theft is a common premise for all Safe-based protocols, not an EigenDA-specific vulnerability. Consistent with Dedaub N1 Informational classification. AV:P -- Simultaneous compromise of 3 independent keys requires physical access or social engineering. AC:H -- 3-of-4 multisig is a security hardening measure; binary BVSS choice (H/L) overrepresents actual difficulty. PR:R -- Signer credentials required. EigenDA-specific findings: (1) No timelock -- execution is immediate with no community response time. (2) Single Safe for 8 core contracts -- no privilege separation. (3) Signer identities not onchain-verified. CIA reflects full control on successful compromise, but Impact downgraded to M -- the compromise scenario itself is governance observation, not an exploit path.",
    },
    "EDA-T09": {
        "title": "Ejector Role Abuse Can Remove Honest Operators",
        "details": "EjectionManager (0x130d8E...) owner=same multisig (0x002721...). The ejector is EOA 0x864247... (a single address, not a multisig). rateLimitWindow=259200 seconds (3 days), ejectableStakePercent=3333 (33.33%). Up to 33.33% of Q0 stake can be ejected within 3 days. Probe measurements: 528 ejection events (~2026-03), peaking at 178 in 2024-08.",
        "prerequisites": "Ejector role abuse",
        "mitigations": "EjectionCooldown configuration.",
        "condition": "",
        "example": "",
        "verification_note": "2 active ejector EOAs called 150 ejections over 16 months (100% of all ejections); quorum 33% ejection possible. Dune query 7461036 tracks OperatorStakeUpdate not ejection. Blockscout 150 events are the primary ejection source.",
        "bvss_rationale": "B:N -- No direct fund theft possible. AV:N -- Onchain transaction. AC:L -- Single EOA key; 150 active uses observed over 16 months. PR:R -- Ejector role. A:H/AI:H -- Can force-eject 33.33% of quorum stake within 3 days.",
    },
    "EDA-T10": {
        "title": "PutAttestation Unconditional Overwrite -- Attestation Integrity Guard Absent (Defense-in-Depth Flaw)",
        "details": "The PutAttestation used by disperser/controller to store attestations in DynamoDB performs an unconditional PutItem without ConditionExpression (attribute_not_exists) -- code comment reads 'Allow overwrite of existing attestation'. This is inconsistent with sibling functions in the same store (PutBlobMetadata, PutBatch) which use attribute_not_exists guards. The controller first writes an empty attestation (line 315), then gathers signatures and writes the final version (line 419); the put failure at line 327 is ignored as 'this error isn't fatal', creating a racing window. Standalone tampering cannot create a valid DACert (onchain checkDACert blocks it; see verification_note). The effective threat is limited to a composite scenario requiring IAM credential theft (or concurrent write contention) combined with the client skipping onchain verification.",
        "prerequisites": "AWS IAM credential theft (or concurrent write contention) + client skipping onchain verification",
        "mitigations": "Add ConditionExpression (attribute_not_exists) or state machine guard to PutAttestation; treat put failure at controller.go:327 as batch fail. Primary defense is onchain checkDACert via mainnet router (0x61692e93b6B045c444e942A91EcD1527F23A3FB7).",
        "condition": "",
        "example": "",
        "verification_note": "Code finding (PutAttestation unconditional overwrite inconsistency) verified from primary source. Security impact is bounded by onchain checkDACert (BLS pairing + Merkle inclusion + stake snapshot 55% + quorum subset, EigenDACertVerificationLib.sol:82-122) -- tampering scenarios a-f,h all revert. signedStake is computed from onchain StakeRegistry, not attestation, so tampering is ineffective. Residual attack surface is limited to (g) IAM theft + client skipping onchain verification composite scenario and the racing window exposure.",
        "bvss_rationale": "B:N -- No financial impact. AV:P -- Requires disperser AWS internal write access. AC:H -- Racing window timing + client skipping onchain verification must both be met. I:M/II:M -- Attestation overwrite possible but onchain checkDACert is primary defense.",
    },
    "EDA-D10": {
        "title": "Unauthenticated POST Bulk Requests Overload Proxy",
        "details": "Proxy HTTP POST has no request count limit. Body size is limited by MaxBytesReader at 16MB. Since the Proxy is a rollup operator's self-operated sidecar, this is only a threat when externally exposed. Same root cause as EDA-D02.",
        "prerequisites": "Access to Proxy endpoint",
        "mitigations": "Only body size limit exists.",
        "condition": "",
        "example": "",
        "verification_note": "Code confirms handlers_cert.go:198 has only MaxBytesReader. Proxy is a rollup sidecar so mainnet external probing is not possible -- code path only. Same root cause as EDA-D02.",
        "bvss_rationale": "B:N -- No financial impact. AV:N. AC:H -- Same root cause as EDA-D02; Proxy is designed as a private sidecar. A:L/AI:L -- Limited to individual rollup operator.",
    },
    "EDA-D12": {
        "title": "11 Dead Operators -- 0% Chunk Serving Response",
        "details": "Prober DB 24-hour measurement: 79 operators probed, 11 dead (0% success), 2 degraded (<90%), 66 healthy. Dead operators include chorus.one, swell-eigenda, attestant.io, among others. They may be signing BLS attestations but not serving chunks (free-riding candidates).",
        "prerequisites": "Operator signs BLS attestations but does not store/serve chunks",
        "mitigations": "Reed-Solomon erasure coding enables recovery despite some operator non-responses. ReconstructionThreshold=22%.",
        "condition": "",
        "example": "",
        "verification_note": "signing-info 1h/24h shows 3 dead. The threat's 11 are based on prober DB (GetChunks) -- 8 gap represents free-rider candidates who sign BLS but don't serve chunks.",
        "bvss_rationale": "B:N -- No direct financial impact. AC:L -- Currently observed (11/79 dead). A:M -- Impacts chunk serving quality. AI:L -- 11/79=13.9%, below Reed-Solomon erasure coding threshold 22%; currently operating within fault tolerance. Conservative note: if slashing remains unimplemented (EDA-P01), dead operator count may increase, but assessed based on current state.",
    },
    "EDA-E03": {
        "title": "Operator Stake Concentration -- Minority Collusion Exceeds Safety/Liveness Thresholds",
        "details": "Onchain verification (block 25097183): Q0 (ETH) top 3 = 39.8% > safety 33%, top 4 = 48.2% > liveness 45%. Q1 (EIGEN) top 3 = 35.6% > safety 33%, top 5 = 51.7% > liveness 45%. Q2 (Custom) AltLayer alone = 52.6%, exceeding all thresholds individually. Q1 top 4-8 contains 5 Coinbase (suspected) entities.",
        "prerequisites": "Q0/Q1: Collusion of 3 operators. Q2: AltLayer alone.",
        "mitigations": "3 independent quorums -- all must fail simultaneously (required quorums = Q0+Q1). However Q2 is not required.",
        "condition": "",
        "example": "",
        "verification_note": "Nakamoto(33)=3, HHI Q0=883/Q1=876, Gini 0.79/0.82. Top5 cumulative Q0=55.25%.",
        "bvss_rationale": "B:N -- Stake concentration itself has no direct financial impact; actual impact only occurs upon collusion execution. AC:H -- Requires organized collusion of 3 independent entities (Q0/Q1 simultaneous). I:M/II:M -- Invalid cert signing possible but onchain BLS verification remains. A:H -- Q0 top3=39.8% exceeds safety 33% confirmed. AI:M -- Both required quorums Q0+Q1 must be compromised simultaneously; single quorum compromise alone cannot halt the entire protocol.",
    },
    "G-CON-03": {
        "title": "Operator Infrastructure (Cloud/ASN) Concentrated in Few Hosting Providers",
        "details": "78 operator host classes extracted (72 raw IP mappings) -> ASN aggregation. Q0 stake: AWS 21.78%, OVH 15.67%, Hetzner, etc. -- top 5 cumulative 82.7%. Q1 stake: Herd SaaS alone 41.87%. A single cloud region/provider outage could bring quorum confirmation threshold (55%) within reach.",
        "prerequisites": "Multiple operators using the same cloud provider/ASN",
        "mitigations": "Geographic/provider diversity incentives, on-prem node supplementation.",
        "condition": "",
        "example": "Herd SaaS Q1 41.87%",
        "verification_note": "AWS 21.78% Q0, Herd SaaS 41.87% Q1. Top5 cumulative Q0=82.7%.",
        "bvss_rationale": "B:N -- No financial impact. AC:H -- Requires specific provider failure conditions. A:H/AI:M -- AWS 21.78% Q0, Herd SaaS 41.87% Q1, top5 cumulative 82.7%; single provider outage approaches quorum confirmation 55% threshold but is transient.",
    },
    "EDA-P01": {
        "title": "EigenDA Operator Slashing Not Implemented -- Asymmetric Honesty Incentives",
        "details": "Zero slash/freeze functions or events across all EigenDA core contracts. EigenLayer AllocationManager shows getOperatorSetCount=0 for EigenDA AVS, with empty arrays for all quorum strategies. ServiceManager slasher()/allocationManager() calls revert. Zero slash events over 500k blocks (~70 days). Only Rewards are wired (rewardsInitiator is an EOA), creating an incentive asymmetry -- operators receive rewards without punishment for dishonest behavior. Directly linked to 8 free-rider candidates in PoC #02.",
        "prerequisites": "EigenLayer slashing not activated + EigenDA's own slasher not implemented",
        "mitigations": "EigenLayer AllocationManager integration, dedicated slasher contract. Ejection is the only current alternative (PoC #02).",
        "condition": "",
        "example": "Operator only signs BLS but does not serve chunks (free-rider) -> zero punishment; only ejection by 2 EOA authorities is available.",
        "verification_note": "EigenDA core .sol has zero slash/freeze instances. AllocationManager OperatorSetCount=0. Zero slash events over 500k blocks. Only rewards are wired.",
        "bvss_rationale": "B:N -- Absence of slashing alone does not prove direct fund theft/freeze path; requires multi-step chain (no slashing -> free-riding -> data withholding -> rollup impact). AC:H -- Requires organized operator free-riding or collusion. S:U -- EigenDA protocol design decision with impact within the same system, not external scope change. I:H/II:M -- DA guarantee integrity gap (undetected data withholding) but KZG proof/erasure coding compensating mechanisms exist. A:L/AI:M -- Gradual service quality degradation possible but not immediate availability disruption.",
    },
    "EDA-P02": {
        "title": "DAS (Data Availability Sampling) Absent -- Clients Rely Entirely on Quorum Trust",
        "details": "The official EigenDA spec explicitly states DAS is not used, and the client retrieval path has no sampling interface. Onchain cert verification only checks BLS aggregate signatures and stake threshold (55%); the client's random shuffle is for load balancing, not cryptographic sampling. This is a different trust model from Celestia (namespaced Merkle + sampling) and Ethereum PeerDAS (column sampling). The 8 free-rider gap from PoC #02 is a direct attack scenario.",
        "prerequisites": "EigenDA's design decision not to adopt DAS (different trust model from Celestia et al.)",
        "mitigations": "KZG opening proof enables partial verification (ValidateBatchV2), but is not sample-based. Whether DAS will be introduced in EigenDA v2/v3 is unspecified.",
        "condition": "",
        "example": "Operator signs BLS claiming data received -> cert valid -> retrieval actually fails for data.",
        "verification_note": "Spec docs/spec/src/introduction.md:27 explicitly states DAS is not used. Code has zero sampling interfaces. Verified from spec/code, not mainnet measurement.",
        "bvss_rationale": "B:N -- No direct financial impact. AC:H -- Non-adoption of DAS is a design decision; exploitation requires operator collusion. I:H/II:M -- Entirely dependent on quorum trust, but KZG opening proof provides partial verification. A:L/AI:M -- Clients cannot independently verify, but the protocol itself operates normally.",
    },

    # ---- Avail ----
    "AVL-D01": {
        "title": "VectorX Single Relayer SPOF -- No Code-Level Rate Limit/Heartbeat",
        "details": "VectorX relayer operates as a single EOA (0x27BF7DE579c5779DBfBB8e9D69999E4d1370787D). nonce=2632, balance=0.82 ETH, code=0x (EOA). checkRelayer=true, approvedRelayers has only this EOA set to true. Code-level verification: SP1Vector.sol commitHeaderRange() has zero block.timestamp references, no cooldown/rate limit/heartbeat/timeout logic (full inheritance chain checked). operator.rs uses LOOP_INTERVAL_MINS=60, BLOCK_UPDATE_INTERVAL=360, PROOF_TIMEOUT_SECS=1800 for client-side interval control only -- no onchain enforcement. setRelayerApproval() emits no events (asymmetric with removeHeaderHash which has HeaderHashRemoved event). Previous relayer 0x3243...2D has approvedRelayers=false (rotation history confirmed). Avg relay interval: 120min, batch size: 358 blocks, gas per commit: 458,612. latestBlock=2975481, headerRangeCommitmentTreeSize=2048, latestAuthoritySetId=753.",
        "prerequisites": "Relayer EOA failure or key compromise -- natural failure alone can trigger this. No onchain staleness detection mechanism.",
        "mitigations": "None -- no relayer replacement mechanism (confirmed by L2BEAT). No onchain heartbeat/timeout. Observability is also limited (setRelayerApproval emits no events).",
        "condition": "",
        "example": "",
        "verification_note": "cast confirmed EOA/nonce/balance/approvedRelayers. SP1Vector.sol source code: commitHeaderRange() has zero rate limit/heartbeat/timeout (full inheritance chain). operator.rs LOOP_INTERVAL_MINS=60 confirmed (no onchain enforcement). setRelayerApproval event absence confirmed. Anvil mainnet fork PoC: (1) single relayer access control (2) staleness detection absence (3) guardian ZK bypass (intended mechanism). Previous relayer 0x3243...2D rotation history confirmed.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:N -- Network level (DDoS, key compromise). AC:L -- Single point of failure; natural failure alone triggers this; zero onchain rate limit/heartbeat (code confirmed). PR:N -- External attacker capable. S:U -- Impact within bridge scope. A:H -- DA attestation bridge completely halted (commitHeaderRange calls impossible). AI:M -- Avail chain data itself remains accessible but unverifiable on Ethereum (verifiable availability lost). No relayer replacement/fallback mechanism.",
    },
    "AVL-E03": {
        "title": "Deployer EOA Retains DEFAULT_ADMIN_ROLE -- Solo VectorX Upgrade Possible",
        "details": "VectorX deployer EOA 0xDEd0000E32f8F40414d3ab3a830f735a3553E18e still holds DEFAULT_ADMIN_ROLE (0x00). TIMELOCK_ROLE/GUARDIAN_ROLE have been revoked (false). However, since DEFAULT_ADMIN_ROLE is the admin of both roles, the deployer can single-handedly execute grantRole(TIMELOCK_ROLE, self) -> upgradeTo(malicious) in 2 transactions to take over VectorX. The deployment script (Guardian.s.sol) has the DEFAULT_ADMIN_ROLE revoke code commented out. Deployer is an EOA (code=0x), nonce=1107 (active account).",
        "prerequisites": "Deployer EOA private key compromise (1 key)",
        "mitigations": "None -- entirely dependent on deployer key security. Guardian.s.sol revoke is commented out.",
        "condition": "",
        "example": "",
        "verification_note": "3 roles x 2 principals exhaustive verification. DEFAULT_ADMIN=true for deployer confirmed. TIMELOCK_ROLE admin=0x00 confirmed. Guardian.s.sol source code: revoke commented out confirmed.",
        "bvss_rationale": "B:N -- Direct fund theft path unproven but bridge funds at risk. AV:N -- Direct call from Ethereum network. AC:H -- Requires deployer EOA private key compromise. PR:R -- Deployer credentials. S:C -- Impact extends beyond VectorX to entire L2/Bridge. I:H/II:H -- Arbitrary implementation replacement -> false attestation, complete multisig bypass. A:H/AI:H -- Complete bridge halt possible; single key bypasses entire governance.",
    },
    "AVL-T01": {
        "title": "VectorX Instant Upgrade (4/7 Multisig, NO Timelock)",
        "details": "Avail Multisig 1 (4/7, 0x7F2f87B0Efc66Fea0b7c30C61654E53C37993666) can instantly upgrade VectorX. EIP-1967 admin slot=0x0 (UUPS pattern, upgrade within implementation). Bridge has 24h timelock applied, but VectorX does not. TimelockedUpgradeable class provides only an AccessControl wrapper without actual timelock (see AVL-S01).",
        "prerequisites": "Obtain 4 of 7 signer keys from Avail Multisig 1",
        "mitigations": "4/7 multisig threshold. However, no timelock.",
        "condition": "",
        "example": "",
        "verification_note": "EIP-1967 admin slot=0x0 confirmed (UUPS). L2BEAT cross-verified. TimelockedUpgradeable source code: delay logic absence confirmed.",
        "bvss_rationale": "B:N -- Direct financial impact uncertain. AV:P -- Obtaining 4/7 multisig keys requires physical/social engineering access. AC:H -- Simultaneous compromise of 4 of 7 signer keys. PR:R -- Multisig signer credentials. S:U -- Within VectorX upgrade scope. I:H/II:M -- Malicious upgrade can forge data roots but community detection possible. A:H/AI:M -- Bridge halt possible but multisig protection exists.",
    },
    "AVL-E04": {
        "title": "Technical Committee Runtime Upgrade (5/5 or 5/7 Consensus)",
        "details": "The Technical Committee can upgrade the mainnet runtime with 5/5 or 5/7 consensus. Transparency Report 16 documents actual usage (block #1,095,300): a 5/5 consensus TC runtime upgrade was applied to fix a send_message logic bug. Full-scope impact: consensus rule changes, staking parameter changes, etc.",
        "prerequisites": "Obtain 5 of 7 Technical Committee member keys",
        "mitigations": "Requires 5/5 or 5/7 consensus. Transparency Reports are published.",
        "condition": "",
        "example": "",
        "verification_note": "Avail Forum Transparency Report 16 confirms TC runtime upgrade usage. block #1,095,300.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- TC 5/7 member key compromise requires physical/social engineering access. AC:H -- Requires 5/7 consensus. PR:R -- TC member credentials. S:C -- Chain-wide consensus rule changes. I:H/II:M -- Arbitrary staking/finality rule changes possible but detectable via Transparency Reports. A:H/AI:M -- Chain halt possible but strict TC consensus requirement.",
    },
    "AVL-T05": {
        "title": "KZG Trusted Setup (Filecoin PoT, 1-of-N Honest Assumption)",
        "details": "Avail KZG uses the Filecoin Powers of Tau ceremony (challenge_19, BLS12-381). Relies on the 1-of-N honest participant assumption. If all ceremony participants were dishonest, validity proof forgery would be possible, but the practical probability is extremely low.",
        "prerequisites": "All ceremony participants dishonest (1-of-N assumption violation)",
        "mitigations": "1-of-N honest participant assumption -- Filecoin PoT ceremony had many participants.",
        "condition": "",
        "example": "",
        "verification_note": "SRS parameter source confirmation needed. Theoretical threat.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:N -- Network. AC:H -- Requires all ceremony participants to be dishonest (1-of-N assumption). PR:N -- Ceremony participant. S:U -- Within KZG verification scope. I:H/II:M -- Validity proof forgery theoretically possible but practical probability extremely low.",
    },
    "AVL-E01": {
        "title": "SP1VerifierGateway 2/3 Multisig -- Verifier Route Manipulation Possible",
        "details": "The multisig controlling SP1 verifier routing (0xCafEf00d348Adbd57c37d1B77e0619C6244C6878) has a 2/3 threshold. Owner #2 (0x72Ff...4f54) is the same person as owner #4 of Avail Multisig 1. Succinct 1 person + Avail 1 person is sufficient to change verifier routes. Replacing the verifier with a tampered contract would allow false ZK proofs to be judged as valid.",
        "prerequisites": "Compromise 2 of 3 SP1VerifierGateway signer keys",
        "mitigations": "Verifier replacement is restricted to SP1VerifierGateway owner only. 2/3 threshold.",
        "condition": "",
        "example": "",
        "verification_note": "getThreshold=2, getOwners 3 confirmed. owner#2=0x72Ff...4f54 cross-verified as identical to Gov Multisig owner#4.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- 2/3 key compromise required (physical/social engineering). AC:H -- Simultaneous compromise of 2 signer keys. PR:R -- Multisig signer credentials. S:U -- Within verifier route change scope. I:H/II:M -- Verifier route change enables false proof acceptance, but 1 overlapping member weakens effective independence.",
    },
    "AVL-T03": {
        "title": "AVAIL Token Mint via Bridge Upgrade -- Unlimited Minting Possible",
        "details": "AVAIL token (0xeeb4d8400aeefafc1b2953e0094134a887c76bd8) is immutable, but mint/burn authority resides in Bridge proxy (0x054f...). totalSupply ~791M AVAIL, owner() reverts (immutable). Via Bridge upgrade (24h timelock) or VectorX upgrade (NO timelock), a malicious upgrade could enable unlimited minting.",
        "prerequisites": "Bridge upgrade (TimelockController + 4/7) or VectorX upgrade (4/7 direct)",
        "mitigations": "Bridge: 24h timelock. VectorX: no timelock but 4/7 multisig.",
        "condition": "",
        "example": "",
        "verification_note": "totalSupply, owner() revert, mint/burn authority limited to Bridge confirmed.",
        "bvss_rationale": "B:N -- No direct financial impact (multisig premise). AV:P -- 4/7 key compromise required. AC:H -- 24h timelock (Bridge) or 4/7 multisig (VectorX). PR:R -- Multisig signer or timelock proposer credentials. S:U -- Within token mint scope. I:H/II:M -- Unlimited minting possible but timelock/multisig protection exists.",
    },
    "AVL-T04": {
        "title": "Guardian updateBlockRangeData() -- Arbitrary Commitment Injection Without ZK Proof (Intended Emergency Mechanism)",
        "details": "SP1Vector.sol's updateBlockRangeData() function allows GUARDIAN_ROLE holders to directly inject arbitrary data/state commitments without ZK proof verification. Normal path: relayer -> commitHeaderRange() -> SP1 ZK proof verification -> commitment stored. Guardian path: multisig -> updateBlockRangeData() -> commitment stored directly without proof. This is an intended emergency recovery mechanism. Additional Guardian capabilities: updateVerifier(), updateVectorXProgramVkey(), updateGenesisState(). GUARDIAN_ROLE = Multisig 1 (4/7).",
        "prerequisites": "GUARDIAN_ROLE holder (Multisig 1, 4/7 key compromise)",
        "mitigations": "GUARDIAN_ROLE = Multisig 1 (4/7). Designed for emergency recovery. Intended mechanism.",
        "condition": "",
        "example": "",
        "verification_note": "SP1Vector.sol source code: updateBlockRangeData() stores commitments directly without ZK proof verification confirmed. Anvil fork PoC-3 confirmed guardian ZK bypass behavior -- this is an intended emergency recovery mechanism.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- 4/7 multisig key compromise required. AC:H -- 4/7 multisig required. PR:R -- GUARDIAN_ROLE required. S:U -- Within commitment storage scope. I:H/II:M -- ZK bypass possible but intended emergency mechanism with 4/7 multisig protection.",
    },
    "AVL-D02": {
        "title": "Validator Set 105/1200 -- Nakamoto Coefficient ~34, 8.75% Utilization",
        "details": "105 active validators out of max 1200 (8.75% utilization). Nakamoto coefficient ~34 (validators needed to control 33.33% stake). Total staked ~4.794B AVAIL (48% of 10B supply). Top validator: 50.79M AVAIL (1.06%), Bottom: 42.4M (0.88%). Max/min ratio: 1.20x -- NPoS Phragmen achieves very even distribution. Top 10 = 10.54% combined. BFT threshold 2/3 = 70 validators colluding could seize finality.",
        "prerequisites": "Collusion or compromise of 34+ validators (33.33% stake)",
        "mitigations": "NPoS Phragmen even distribution (1.2x variance). Nakamoto 34 = 1/3 of set.",
        "condition": "",
        "example": "",
        "verification_note": "Session.Validators storage=105. Subscan Era #688 stake distribution directly calculated. Nakamoto~34, top 1.06%, max/min 1.20x.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:N -- Network. AC:H -- 34+ validator collusion required. PR:N -- Validator credentials obtainable. S:U -- Within chain finality scope. A:H -- Finality disruption possible. AI:M -- Phragmen even distribution (1.2x) limits stake concentration; practical collusion difficulty is high.",
    },
    "AVL-I01": {
        "title": "Block Reconstruction Incomplete -- DAS Security Guarantees Theoretical",
        "details": "Light client DAS is implemented, but the block reconstruction protocol is under development. The protocol for recovering full blocks from minimal light nodes is incomplete. DAS security guarantees exist only theoretically. Data availability sampling operates at 99.84% confidence (Observatory measurement), but reconstruction depends on full nodes.",
        "prerequisites": "Data reconstruction failure when full nodes are absent",
        "mitigations": "Multiple full nodes exist (40 peers). DAS itself is operational.",
        "condition": "",
        "example": "",
        "verification_note": "Documentation-based assessment. Code review needed for adjustment. Indirectly verified through Observatory DAS data.",
        "bvss_rationale": "B:N -- No financial impact. AV:N -- Network. AC:H -- Only occurs when full nodes are absent; currently 40 peers exist. PR:N -- Anyone can attempt reconstruction. S:U -- Within DAS security scope. C:L/CI:L -- Some information access limited if data recovery fails.",
    },
    "AVL-E02": {
        "title": "Multisig Key Holder Triple Overlap (Gov + Pauser + SP1)",
        "details": "Severe key holder overlap across 3 multisigs. Pauser Multisig (0x1a5b...8930, 3/5): 4 of 5 owners are identical to Governance Multisig 1. SP1VerifierGateway (0xCafE...6878, 2/3): 1 owner (0x72Ff...4f54) is identical across Gov + Pauser. 0x72Ff26D9517324eEFA89A48B75c5df41132c4f54 participates in all 3 multisigs (Gov #4, Pauser #4, SP1 #2). Pauser threshold 3/5: with 4 overlapping members, 3 governance keys can trigger pause.",
        "prerequisites": "Governance multisig compromise automatically impacts Pauser + SP1",
        "mitigations": "Separate thresholds per multisig (4/7, 3/5, 2/3).",
        "condition": "",
        "example": "",
        "verification_note": "Pauser Multisig discovered via RoleGranted event tracing. getOwners cross-analysis. 4/5 overlap + 0x72Ff triple participation confirmed.",
        "bvss_rationale": "B:N -- No financial impact. AV:P -- Multisig key compromise required. AC:H -- Multiple simultaneous key compromises. PR:R -- Signer credentials. S:U -- Internal governance issue. I:L/II:L -- Pause independence lost but not a direct attack path. A:L/AI:L -- Emergency response delay.",
    },
    "AVL-R01": {
        "title": "Slashing Infrastructure Exists but Not Triggered in 688 Eras",
        "details": "Avail NPoS slashing infrastructure exists in code but has never been triggered. Runtime metadata has 67 references to 'slash'. SlashDeferDuration=27 eras, BondingDuration=28 eras, SessionsPerEra=6. ActiveEra=688 (long-running). UnappliedSlashes(era=688)=empty (not triggered). Zero slashing events across 688 eras means no practical sanctions for validator misbehavior.",
        "prerequisites": "Internal validator behavior concern -- not a direct external attack",
        "mitigations": "Slashing infrastructure code exists. BondingDuration=28 eras.",
        "condition": "",
        "example": "",
        "verification_note": "ActiveEra SCALE decode=688. UnappliedSlashes=null (empty). Runtime constants confirmed.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- Internal validator behavior concern. AC:L -- Non-triggering is the permanent state. PR:R -- Validator credentials. S:U -- Within incentive scope. A:L/AI:L -- Indirect incentive weakening impact.",
    },
    "AVL-T02": {
        "title": "Bridge 24h Timelock -- Relatively Safe, Limited Risk",
        "details": "Bridge upgrades route through TimelockController (0x45828180bbE489350D621d002968A0585406d487) with getMinDelay=86400 (24h). DEFAULT_ADMIN=TimelockController. TimelockController proposer/executor=Multisig 1 (0x7F2f...). Users can exit within 24h.",
        "prerequisites": "TimelockController proposer (Multisig 1, 4/7) key compromise + 24h wait",
        "mitigations": "24h timelock -- user exit time guaranteed. 4/7 multisig threshold.",
        "condition": "",
        "example": "",
        "verification_note": "TimelockController DEFAULT_ADMIN confirmed. getMinDelay=86400 (24h) confirmed.",
        "bvss_rationale": "B:N -- No direct financial impact. AV:P -- 4/7 key compromise required. AC:H -- 4/7 + 24h wait. PR:R -- Proposer credentials. S:U -- Timelock limits impact scope. I:L/II:L -- User exit possible within 24h, limiting practical risk.",
    },
    "AVL-S01": {
        "title": "TimelockedUpgradeable Name Misleading -- No Actual Timelock",
        "details": "VectorX's upgrade base class TimelockedUpgradeable contains no actual timelock logic. It is simply an AccessControl wrapper using the name TIMELOCK_ROLE. The onlyTimelock modifier only checks hasRole(TIMELOCK_ROLE, msg.sender). No actual delay, queue, or execute pattern exists. Source: succinctlabs/succinctx submodule, contracts/src/upgrades/TimelockedUpgradeable.sol.",
        "prerequisites": "None -- discovered through static code analysis",
        "mitigations": "None -- the code name vs. functionality mismatch is itself the issue.",
        "condition": "",
        "example": "",
        "verification_note": "Source code confirmed: delay logic absent. onlyTimelock = hasRole check only.",
        "bvss_rationale": "No direct CIA impact. ISS=0 so Base Score=0. Classified as Informational due to security perception misdirection risk.",
    },
}


# ---------------------------------------------------------------------------
# Reference parsing
# ---------------------------------------------------------------------------

EIGENDA_COMMIT = "ec2ce8ab"
EIGENDA_REPO = "Layr-Labs/eigenda"
AVAIL_REPO = "availproject/sp1-vector"


def parse_references(refs_str: str, protocol: str) -> str:
    """Parse the references string into formatted markdown."""
    if not refs_str or not refs_str.strip():
        return "None specified."

    entries = [r.strip() for r in refs_str.split(",") if r.strip()]

    code_refs = []
    poc_refs = []
    audit_refs = []
    onchain_refs = []
    other_refs = []

    for entry in entries:
        if entry.startswith("code:"):
            code_refs.append(entry[5:])
        elif entry.startswith("poc:"):
            poc_refs.append(entry[4:])
        elif entry.startswith("audit_consolidated:") or entry.startswith("audit:"):
            audit_refs.append(entry.split(":", 1)[1])
        elif entry.startswith("onchain:"):
            onchain_refs.append(entry[8:])
        elif entry.startswith("source:"):
            other_refs.append(entry[7:])
        elif entry.startswith("cast:"):
            onchain_refs.append(entry[5:])
        elif entry.startswith("prober:"):
            other_refs.append("Prober: " + entry[7:])
        elif entry.startswith("grpcurl:"):
            other_refs.append("gRPC probe: " + entry[8:])
        elif entry.startswith("dfd:"):
            other_refs.append("DFD: " + entry[4:])
        elif entry.startswith("doc:"):
            other_refs.append(entry[4:])
        elif entry.startswith("RPC:"):
            onchain_refs.append(entry[4:])
        elif entry.startswith("L2BEAT:"):
            other_refs.append("L2BEAT: " + entry[7:])
        elif entry.startswith("Subscan:"):
            onchain_refs.append("Subscan: " + entry[8:])
        elif entry.startswith("observatory:"):
            other_refs.append("Observatory: " + entry[12:])
        elif entry.startswith("ipinfo.io"):
            other_refs.append(entry)
        elif entry.startswith("README.md:"):
            other_refs.append(entry)
        elif entry.startswith("spec:"):
            other_refs.append(entry[5:])
        else:
            other_refs.append(entry)

    lines = []

    if code_refs:
        lines.append("### Source Code\n")
        for ref in code_refs:
            # Separate inline annotation after " — " (em-dash with spaces)
            annotation = ""
            ref_main = ref
            if " — " in ref:
                idx = ref.index(" — ")
                annotation = " -- " + ref[idx + 3:]
                ref_main = ref[:idx]
            elif " — " not in ref and "(" in ref:
                # Handle parenthetical notes like "cli.go:47(기본 0.0.0.0)"
                idx = ref.index("(")
                annotation = " -- " + ref[idx + 1:].rstrip(")")
                ref_main = ref[:idx]

            # Parse path:lines — handle multi-line specs like "54,257,67"
            # Match pattern: filepath.ext:linespec
            m = re.match(r'^(.+\.\w+):(\d[\d,\-]*)$', ref_main.strip())
            if m:
                path = m.group(1).strip()
                line_spec = m.group(2).strip()
                if protocol == "eigenda":
                    line_anchor = ""
                    # Take only the first range/number for the anchor
                    first_line = line_spec.split(",")[0]
                    if "-" in first_line:
                        start, end = first_line.split("-", 1)
                        line_anchor = f"#L{start}-L{end}"
                    elif first_line.isdigit():
                        line_anchor = f"#L{first_line}"
                    url = f"https://github.com/{EIGENDA_REPO}/blob/{EIGENDA_COMMIT}/{path}{line_anchor}"
                    lines.append(f"- [`{path}:{line_spec}`]({url}){annotation}")
                else:
                    url = f"https://github.com/{AVAIL_REPO}/blob/main/{path}"
                    lines.append(f"- [`{path}:{line_spec}`]({url}){annotation}")
            else:
                # No line number — just a file path (possibly with annotation)
                path = ref_main.strip()
                if protocol == "eigenda":
                    url = f"https://github.com/{EIGENDA_REPO}/blob/{EIGENDA_COMMIT}/{path}"
                    lines.append(f"- [`{path}`]({url}){annotation}")
                else:
                    url = f"https://github.com/{AVAIL_REPO}/blob/main/{path}"
                    lines.append(f"- [`{path}`]({url}){annotation}")

    if audit_refs:
        lines.append("\n### Audit References\n")
        for ref in audit_refs:
            lines.append(f"- {ref}")

    if onchain_refs:
        lines.append("\n### Onchain Evidence\n")
        for ref in onchain_refs:
            lines.append(f"- `{ref}`")

    if poc_refs:
        lines.append("\n### PoC Notes\n")
        for ref in poc_refs:
            lines.append(f"- {ref}")

    if other_refs:
        lines.append("\n### Other References\n")
        for ref in other_refs:
            if ref.startswith("http"):
                lines.append(f"- [{ref}]({ref})")
            else:
                lines.append(f"- {ref}")

    return "\n".join(lines) if lines else "None specified."


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def generate_page(threat: dict, protocol: str) -> str:
    """Generate a single threat markdown page."""
    sid = threat["SID"]
    t = TRANSLATIONS.get(sid, {})

    title = t.get("title", threat.get("description", sid))
    details = t.get("details", threat.get("details", ""))
    prerequisites = t.get("prerequisites", threat.get("prerequisites", ""))
    condition = t.get("condition", threat.get("condition", ""))
    example = t.get("example", threat.get("example", ""))
    mitigations_text = t.get("mitigations", threat.get("mitigations", ""))
    verification_note = t.get("verification_note", threat.get("verification_note", ""))
    bvss_rationale = t.get("bvss_rationale", threat.get("bvss_rationale", ""))

    bvss_score = threat.get("bvss_score", "N/A")
    bvss_severity = threat.get("bvss_severity", "N/A")
    bvss_vector = threat.get("bvss_vector", "N/A")
    likelihood = threat.get("Likelihood Of Attack", "Unrated")
    scope = threat.get("scope", "N/A")
    verification_status = threat.get("verification_status", "unverified")
    targets = threat.get("target", [])
    verified_by_poc = threat.get("verified_by_poc", [])

    stride = stride_letter(sid)
    target_str = ", ".join(targets)

    # Status display
    status_map = {
        "verified": "Verified",
        "code_verified": "Code Verified",
        "partial": "Partially Verified",
        "unverified": "Unverified",
    }
    status_display = status_map.get(verification_status, verification_status)

    # Build references
    refs_str = threat.get("references", "")
    references_md = parse_references(refs_str, protocol)

    # Build attack scenario
    attack_scenario = ""
    if condition and condition.strip():
        attack_scenario += f"**Trigger condition**: `{condition}`\n\n"
    if example and example.strip():
        attack_scenario += example
    if not attack_scenario.strip():
        attack_scenario = "See details above."

    # Build PoC references
    poc_section = ""
    if verified_by_poc:
        poc_list = ", ".join(verified_by_poc)
        poc_section = f"\n**PoC References**: {poc_list}\n"

    md = f"""# {sid}: {title}

{{% hint style="info" %}}
**Severity**: {bvss_severity} ({bvss_score}/10) · **STRIDE**: {stride} · **Scope**: {scope} · **Status**: {status_display}
{{% endhint %}}

## Overview

{details}

## Prerequisites

{prerequisites if prerequisites else "None specified."}

## Attack Scenario

{attack_scenario}

## Impact

| Metric | Value |
|--------|-------|
| BVSS Score | {bvss_score}/10 ({bvss_severity}) |
| BVSS Vector | `{bvss_vector}` |
| Likelihood | {likelihood} |
| Scope | {scope} |
| Target | {target_str} |

### BVSS Rationale

{bvss_rationale}

## Code References

{references_md}

## Verification & Evidence

**Status**: {status_display}

{verification_note}
{poc_section}
## Mitigations

{mitigations_text}
"""
    return md


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    eigenda_json = "/Users/jyoo/work/bonda/bonda-frontend/lib/data/eigenda-threats.json"
    avail_json = "/Users/jyoo/work/bonda/bonda-frontend/lib/data/avail-threats.json"

    eigenda_out = "/Users/jyoo/bonda-docs/eigenda/threats"
    avail_out = "/Users/jyoo/bonda-docs/avail/threats"

    os.makedirs(eigenda_out, exist_ok=True)
    os.makedirs(avail_out, exist_ok=True)

    # Load threats
    with open(eigenda_json, "r", encoding="utf-8") as f:
        eigenda_threats = json.load(f)
    with open(avail_json, "r", encoding="utf-8") as f:
        avail_threats = json.load(f)

    count = 0
    errors = []

    # Generate EigenDA pages
    for threat in eigenda_threats:
        sid = threat["SID"]
        filename = sid.lower() + ".md"
        filepath = os.path.join(eigenda_out, filename)

        if sid not in TRANSLATIONS:
            errors.append(f"WARNING: No translation for {sid}")

        md = generate_page(threat, "eigenda")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        count += 1
        print(f"  [eigenda] {filename}")

    # Generate Avail pages
    for threat in avail_threats:
        sid = threat["SID"]
        filename = sid.lower() + ".md"
        filepath = os.path.join(avail_out, filename)

        if sid not in TRANSLATIONS:
            errors.append(f"WARNING: No translation for {sid}")

        md = generate_page(threat, "avail")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        count += 1
        print(f"  [avail]   {filename}")

    print(f"\nGenerated {count} threat pages.")
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
