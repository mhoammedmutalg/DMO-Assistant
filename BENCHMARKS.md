# BENCHMARKS.md — DMO Assistant

All values below are from the actual zero-key harness run unless explicitly marked otherwise.

| Step | Cost (SAR) | Change | Eval verdict |
|---|---:|---:|---|
| Before: 100 FAQ calls | 0.037571 | baseline | PASS |
| After: exact response cache | 0.000870 | -97.7% | PASS |

- Prompt cache observed on second identical stable-prefix call: 69.7% cached input tokens.
- Exact cache key changes when prompt version changes: True.
- Near-miss wrong hits: 0.
- Guard block rate / false-positive rate: 100.0% / 0.0%.
- Baseline golden set: 120/120 PASS.
- Open-weight harness route: 120/120 PASS.
- Seeded regression: 100/120 -> BLOCKED.

## Break-even status
The measured local rule-backend throughput (9142087 tokens/s) is **not GPU throughput**, so it is deliberately not converted into a self-host break-even. The final submission should run the same benchmark against the actual open-weight GPU backend and then compute SAR/Mtoken from measured throughput and sustained utilization.
