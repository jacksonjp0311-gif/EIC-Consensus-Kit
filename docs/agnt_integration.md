# AGNT Integration

AGNT can use EIC Consensus Kit as the distributed continuity counterpart to a normal agent capability gate.

## Practical Placement

```text
AGNT cycle completes
  -> each node signs or attests to ledger root
  -> subgroup weights and drift are recorded
  -> compression policy and retained proofs are recorded
  -> eicg evaluate runs
  -> outcome is stored in the AGNT ledger
```

Before evaluation, AGNT can validate shape and produce proof material:

```powershell
eicg validate-schema audits/eic_record.json
eicg merkle-root ledgers/cycle_records.json
eicg merkle-proof ledgers/cycle_records.json 42
eicg evaluate audits/eic_record.json --fail-under 0.85
```

## Registry Policy

| Outcome | AGNT action |
| --- | --- |
| `EIC-A` | Promote distributed continuity claim for the stated boundary. |
| `EIC-B` | Allow guarded use; expose required actions. |
| `EIC-C` | Treat as single-node or non-distributed continuity. |
| `EIC-D` | Keep experimental; do not promote distributed trust. |
| `EIC-E` | Reject the distributed continuity claim. |

## Example Use

AGNT can use this to decide whether a multi-agent memory ledger is trustworthy enough to become the canonical history for a capability, plugin, or collective state.

It should reject:

- unsigned quorum,
- hidden disagreement,
- weight changes without policy,
- unnormalized weights,
- pruning without retained proof,
- claims that consensus proves truth or sentience.

## Signature Path

For stronger attestations, AGNT should sign the message:

```text
node_id:accepted_root
```

using Ed25519. The record can then include each node's public key and signature. EIC Consensus Kit verifies those signatures when the optional `cryptography` dependency is installed.
