# Atlas-Research eval rubric

A trace **passes** when:

1. Final report cites **at least `expected_sources_min`** independent
   sources.
2. Every cited claim is **direct or partial** (no tangential, no
   unsupported).
3. The faithfulness gate runs and is green (or explicit
   `LBL-ATLAS-OVERRIDE` annotation when user-overridden).
4. No invented claims (no claim outside the cited evidence span).

Aggregate metrics:

- **Citation density** — citations per claim (target ≥1.0).
- **Faithfulness rate** — fraction of claims surviving the gate
  (target ≥0.90).
- **Dual-source coverage** — fraction of load-bearing claims with
  ≥2 independent sources (target ≥0.70).
- **Invention rate** — fraction of claims outside the cited evidence
  (target 0; non-negotiable).
