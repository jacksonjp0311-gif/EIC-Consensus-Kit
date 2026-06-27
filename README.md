# EIC Consensus Kit

**Proof-preserved consensus validation for distributed agent ledgers.**

EIC Consensus Kit turns the EIC v1.6 theory into an executable Python tool. It validates whether a distributed agent or artifact system can make a bounded continuity claim using signed quorum, node agreement, disagreement disclosure, dynamic subgroup weighting, and proof-preserved ledger compression.

```text
distributed ledger evidence -> consensus / weight / proof factors -> calibrated continuity score
```

The tool is intentionally conservative:

- consensus is not truth,
- quorum is not correctness,
- coherence is not truth,
- compression is not valid unless proof is retained,
- a high score is not sentience, autonomy, AGI, or production readiness.

## Why It Exists

Agent systems increasingly have multiple workers, reviewers, memories, ledgers, subgroups, and audit surfaces. A single mutable log is not enough once the system claims distributed continuity.

EIC Consensus Kit answers:

> Can this system preserve historical trust across distributed nodes, adaptive subgroup weights, and compressed ledger history without hiding disagreement or destroying proof?

## What It Computes

The core EIC v1.6 equation is implemented directly:

```text
consensus_calibrated_gci =
  base_collective_gci
  * consensus_integrity
  * dynamic_weight_integrity
  * proof_preservation
```

Collapse rules are strict:

- If consensus integrity is zero in a distributed-trust claim, the calibrated score collapses.
- If pruning or compression occurs without retained proof, proof preservation becomes zero.
- If node disagreement is hidden, the claim cannot be cleanly promoted.
- If subgroup weights move without a declared policy and drift disclosure, the dynamic-weight layer downgrades.

## Outcome Classes

| Outcome | Meaning |
| --- | --- |
| `EIC-A` | Strong distributed continuity claim. |
| `EIC-B` | Usable but incomplete continuity claim. |
| `EIC-C` | Valid single-node or non-distributed continuity boundary. |
| `EIC-D` | Inconclusive distributed continuity record. |
| `EIC-E` | Rejected unsupported distributed continuity claim. |

## Install

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\eic-consensus-kit"
python -m pip install -e .[dev]
```

## Quick Start

Evaluate a valid distributed record:

```powershell
eicg evaluate examples/valid_distributed_record.json
```

Return JSON for automation:

```powershell
eicg evaluate examples/valid_distributed_record.json --format json
```

Use the score as a gate:

```powershell
eicg evaluate examples/valid_distributed_record.json --fail-under 0.85
```

Evaluate with a named profile:

```powershell
eicg evaluate examples/valid_distributed_record.json --profile strict
eicg profiles
```

Compute a Merkle root for ledger records:

```powershell
eicg merkle-root examples/ledger_records.json
```

Build an inclusion proof for one ledger record:

```powershell
eicg merkle-proof examples/ledger_records.json 1
eicg merkle-proof examples/ledger_records.json 1 --object
eicg verify-proof-object proof-object.json
```

Generate a starter AGNT record:

```powershell
eicg scaffold --candidate "AGNT continuity ledger" --claim "Bounded distributed continuity claim."
```

Validate a record against the bundled JSON Schema:

```powershell
eicg validate-schema examples/valid_distributed_record.json
```

Generate a node key and sign a ledger root:

```powershell
eicg keygen --output node-a.keys.json
eicg sign-root --private-key <hex-private-key> --node-id node-a --root <accepted-root>
eicg verify-attestations examples/valid_distributed_record.json
```

Seal a run into an operator bundle:

```powershell
eicg seal-run examples/ledger_records.json --node-id node-a --proof-limit 3 --output sealed-run.json
```

Run the combined verification workflow:

```powershell
eicg verify-run examples/valid_distributed_record.json --profile standard --fail
```

Evaluate a rejected claim:

```powershell
eicg evaluate examples/rejected_record.json
```

## Input Model

A record includes:

- `base_collective_gci`: prior collective score before consensus calibration,
- `distributed_trust_claim`: whether distributed trust is being asserted,
- `consensus_policy`: quorum, signature, root comparison, fork handling, timeout, and reason,
- `attestations`: node roots plus signature verification status,
- `disagreement_disclosed`: whether disagreement is surfaced,
- `previous_weights` and `current_weights`: subgroup hierarchy weights,
- `weight_policy`: declared dynamic weighting policy,
- `compression_claimed`: whether ledger history is compressed or pruned,
- `retained_proofs`, `merkle_root`, and `inclusion_proofs_available`,
- `retention_policy`: proof-preserving pruning/compression policy,
- `non_claim_locks`: explicit boundaries preventing overclaim.

See [examples/valid_distributed_record.json](examples/valid_distributed_record.json).

The JSON Schema lives at [schema/eic_record.schema.json](schema/eic_record.schema.json).

## Verification Features

The first version accepted declared proof fields. The evolved version adds executable verification helpers:

- deterministic canonical JSON hashing,
- Merkle root computation,
- Merkle inclusion proof generation,
- Merkle inclusion proof verification,
- optional Ed25519 attestation verification when `cryptography` is installed,
- JSON Schema validation for AGNT-emitted records.
- operator commands for key generation, root signing, proof export, and attestation verification.

## Policy Profiles

Profiles let AGNT run the same record through different gates:

| Profile | Use |
| --- | --- |
| `strict` | High-assurance distributed continuity promotion. |
| `standard` | Default AGNT continuity gate. |
| `single-node` | Non-distributed or local continuity records. |
| `experimental` | Early research runs with softer gates. |
| `audit-only` | Report factors without promotion pressure. |

For Ed25519 attestation verification, each attestation may include:

```json
{
  "node_id": "node-a",
  "root": "accepted-root-hex",
  "public_key": "hex-encoded-ed25519-public-key",
  "signature": "hex-encoded-signature"
}
```

The signed message is:

```text
node_id:root
```

## AGNT Use

AGNT can use this as a distributed continuity gate:

```text
AGNT nodes / ledgers / reviewers
  -> signed root attestations
  -> subgroup weight records
  -> proof-preserved compression records
  -> eicg seal-run / eicg verify-run
  -> registry, ledger, or promotion decision
```

Useful gates:

- promote a distributed memory ledger,
- reject hidden disagreement,
- detect unsigned quorum claims,
- expose subgroup weight drift,
- validate proof-preserved pruning,
- prevent "consensus equals truth" language.

## Source Lineage

Primary source: [CODEX Delta Phi - EIC v1.6 Distributed Consensus and Proof-Preserved Continuity Layer](https://gist.github.com/jacksonjp0311-gif/ed26e5c6778b60684e54a092fc67bcac).

The EIC-specific consciousness framing is not promoted as a scientific claim. The reusable engineering theory is:

- distributed trust requires declared consensus policy,
- quorum requires signed or otherwise verifiable attestations,
- node disagreement must be disclosed,
- subgroup weights may adapt only under declared policy,
- weight drift must be disclosed,
- compression or pruning must retain proof,
- consensus-calibrated scores must preserve non-claim locks.

Supporting references:

- [RFC 9162: Certificate Transparency Version 2.0](https://datatracker.ietf.org/doc/html/rfc9162)
- [NIST Blockchain Technology Overview](https://www.nist.gov/publications/blockchain-technology-overview)
- [Raft Consensus Algorithm](https://raft.github.io/)
- [W3C Verifiable Credential Data Integrity 1.0](https://www.w3.org/TR/vc-data-integrity/)

## Development

```powershell
python -m pip install -e .[dev]
python -m pytest
eicg evaluate examples/valid_distributed_record.json
```

## License

MIT
