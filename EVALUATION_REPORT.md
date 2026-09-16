# EVALUATION_REPORT.md — DMO Assistant

## Executive summary
This report is generated from the reproducible zero-key rule-based harness run in this project environment. It validates the application pipeline and safety/evaluation mechanics. It is **not** a claim about a live commercial provider or a GPU-hosted model.

## Golden set
- Cases: 120
- Baseline passed: 120/120 (100.0%)
- Arabic slice: 100.0%
- English slice: 100.0%
- Safety slice: 100.0%
- Golden set is versioned as `data/golden_set.v1.yaml` and stratified by language, intent, difficulty and risk.

## Guard evaluation
- Attack block rate: 100.0%
- Legitimate false-positive rate: 0.0%
- Saudi PII sample after masking: `Employee 1001 email [MASKED_EMAIL] mobile [MASKED_MOBILE] national id [MASKED_NATIONAL_ID]`
- Outbound wall checks canary/system-prompt leakage and outbound PII.

## Structured output and tool safety
- Validate/repair demonstration required 2 attempts.
- Repeated side effect returned the same request id: True.
- Unauthorized side effect blocked: True.
- Tool loop is bounded and tested with tool result returned to the model boundary.

## Judge calibration
- Written rubric: `prompts/judge_groundedness.v1.md`
- Human labels: 40
- Agreement: 100.0%
- Cohen's kappa: 1.00
- In this local run the judge route is the deterministic zero-key backend. A live-provider calibration run must be captured before claiming provider-specific judge quality.

## Regression gate
Baseline verdict: PASS. Seeded `faq.v2-broken` result: 100/120 (83.3%). Gate verdict: **BLOCKED**.

Failed seeded slices include FAQ 60.0%, hard 75.0%, and normal-risk 75.0%, while safety remains 100.0%.

## Backend comparison in reproducible harness
| Slice | Commercial route | Open-weight route |
|---|---:|---:|
| Overall | 100.0% | 100.0% |
| Arabic | 100.0% | 100.0% |
| English | 100.0% | 100.0% |
| Safety | 100.0% | 100.0% |

These are deterministic harness routes, not measured live-model quality. The provider SDK adapter is included for the submission environment.

## Known limitations
1. The execution environment used to generate this report has no network access and could not install or call the official OpenAI SDK. The project includes an isolated `OpenAIProviderAdapter` that uses the official SDK and strict JSON schema when run in Colab with the dependency available, but its live-provider results are not fabricated here.
2. The open-weight route in this report is a deterministic local backend, not measured GPU inference; therefore the local rule-backend throughput is not used as a self-host GPU break-even claim.
3. The DMO knowledge corpus is intentionally small and demonstrative.
4. Semantic caching is conservatively disabled in the zero-key harness; the near-miss suite records zero wrong hits, but a production semantic threshold still requires embedding measurements.
5. Human-label calibration data is synthetic project evaluation data and should be replaced/approved by domain reviewers for a real pilot.
