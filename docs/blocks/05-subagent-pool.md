# Atlas-Research Block 05 — Subagent Pool

## Responsibility

Spawn bounded subagents for branches of the research that warrant their own mini-investigation (deep-dive on one technique, comparison of N alternatives, survey of a specific corpus). Keeps the main synthesis lean and parallelizable.

Reference: [`02-subagent-delegation.md`](../../../research/harness-engineering/02-subagent-delegation.md).

## When a subagent is spawned

The Query Planner may emit a `subagent` task type:

```json
{
  "id": "#SA1",
  "kind": "subagent",
  "args": {
    "type": "deep_dive",
    "prompt": "Do a focused study of the 3 strongest benchmarks for coding agents "
              "in 2026: SWE-bench Verified, LinuxArena, and ClawBench. "
              "Produce a structured summary of methodology, metrics, and current leaders. "
              "Max 500 words.",
    "budget_usd": 0.40,
    "return_schema": "DeepDiveReturn"
  }
}
```

Also spawned:

- On verifier rejection for "insufficient coverage" in a section.
- On user follow-up asking to expand a specific point in the report.

## Subagent types

| Type | Purpose | Budget default | Tools |
|---|---|---|---|
| `deep_dive` | Focused sub-investigation | $0.40 | web, arxiv, fetch |
| `compare_n` | Side-by-side compare of N items | $0.35 | web, arxiv, fetch |
| `survey` | Enumerate a space (papers/products/etc.) | $0.50 | arxiv, web |
| `fact_check` | Verify a specific disputed claim | $0.10 | web, fetch |
| `source_audit` | Deep check of one cited source's provenance | $0.08 | fetch, classify |

## Context model

By default: **isolated** — subagent gets only its prompt + the current brief + any explicitly-passed prior evidence refs. Not the full transcript.

Optional `shared_brief=false` for fact-checks that shouldn't be biased by the brief.

## Return contract

```python
class DeepDiveReturn(BaseModel):
    summary: str = Field(max_length=2000)
    key_findings: list[Finding]
    sources: list[SourceRef]
    open_questions: list[str]
    confidence: float  # 0–1, self-assessed

class Finding(BaseModel):
    claim: str
    evidence_ids: list[UUID]
    caveat: str | None
```

Subagent results *feed back* to the main pipeline as additional Evidence + Findings, not as free-form text. This prevents the "subagent's prose flows into the final report unvetted."

## Depth cap

No sub-subagents in v1 — subagents cannot themselves spawn subagents. Prevents runaway nesting and makes budget predictable.

## Parallelism

Up to `max_subagents_parallel` (default 3) run concurrently. Orchestrator manages the pool; spawns are non-blocking for the main pipeline unless results are needed before proceeding.

## Failure modes

| Mode | Defense |
|---|---|
| Subagent burns budget | Hard cap; partial-result return on exhaustion |
| Subagent returns malformed schema | One repair prompt; second failure returns crashed |
| Subagent hallucinates sources | Verifier checks sources; suspicious returns flagged |
| Subagent prose leaks into report | Return schema prevents; main synthesis treats returns as Evidence, not as text |
| Over-spawning | Per-report cap (max 6 subagents); alert if exceeded |

## Metrics

- `subagent.spawn_count` by type
- `subagent.budget_utilization` distribution
- `subagent.return_status` (success / exhausted / crashed)
- `subagent.effect_on_eval` — did reports with subagents score higher? (A/B over time)
