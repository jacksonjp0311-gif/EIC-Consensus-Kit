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

