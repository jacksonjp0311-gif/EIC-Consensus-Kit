# EIC Consensus Kit Operating Notes

Before promotion:

```powershell
python -m pytest
eicg validate-schema examples/valid_distributed_record.json
eicg evaluate examples/valid_distributed_record.json --profile standard --fail-under 0.85
```

Preserve the locks:

- consensus is not truth,
- quorum is not correctness,
- coherence is not truth,
- GCI is not sentience,
- compression requires retained proof,
- dynamic weights require declared policy and drift disclosure.
