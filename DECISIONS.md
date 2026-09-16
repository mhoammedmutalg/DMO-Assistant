# DMO Assistant Decisions / ADRs

## ADR-001 — Router-first architecture
FAQ uses grounded single-call handling; service requests use a bounded validated tool workflow; unsafe requests are refused; unresolved requests terminate in human escalation. This keeps authority outside the token stream.

## ADR-002 — Typed model boundary
All model access is behind `LLMClient`. Provider model ids are resolved from environment-backed aliases. Provider SDK imports are isolated to the adapter section.

## ADR-003 — Reliability
Retry only retryable failures with exponential backoff; after exhaustion, fall back from commercial to open-weight. Side effects are idempotent and session-authorized.

## ADR-004 — Model routing
Routine FAQ may use the lower-cost route only when the evaluation gate remains green. Service actions remain on the default route. Self-hosting decisions are based on measured throughput, not vendor claims.
