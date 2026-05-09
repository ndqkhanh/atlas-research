# Atlas-Research Block 02 — Query Planner

## Responsibility

Convert a Research Brief into a finite, parallelizable DAG of retrieval and fetch tasks. The planner emits placeholders for tool outputs (ReWOO style) so the executor can fan out without waiting on the LLM between tasks.

Reference: [`17-rewoo.md`](../../../research/harness-engineering/17-rewoo.md).

## Inputs & outputs

- **Input:** Research Brief + source registry (what sources are available in this deployment).
- **Output:** `QueryPlan` — a list of `QueryTask`s with explicit `depends_on` references.

## Planner protocol

One LLM call to a strong model (Opus / o-class), prompted to emit JSON:

```json
{
  "tasks": [
    {"id": "#E1", "kind": "web_search",
     "args": {"query": "harness engineering Claude Code leak 2026"}},
    {"id": "#E2", "kind": "arxiv_search",
     "args": {"query": "agentic AI harness long-running"}},
    {"id": "#E3", "kind": "fetch_url",
     "args": {"url": "{#E1[0].url}"},
     "depends_on": ["#E1"]},
    {"id": "#E4", "kind": "arxiv_get",
     "args": {"arxiv_id": "{#E2[0].arxiv_id}"},
     "depends_on": ["#E2"]},
    {"id": "#E5", "kind": "kb_query",
     "args": {"corpus": "internal", "query": "..."}}
  ],
  "estimated_cost_usd": 1.80,
  "coverage_note": "Covers harness architectures and recent papers; "
                   "may under-represent industry essays."
}
```

Placeholders (`{#E1[0].url}`) bind to earlier results at executor time — no LLM round-trip needed.

## DAG shape rules

- Max depth: default 3 (prevents runaway planning cascades).
- Independent branches preferred; the planner is instructed to parallelize.
- Total task cap: default 30 (raises to 60 for `style=exhaustive`).
- Budget pre-check: planner's `estimated_cost_usd` is compared to the request's cap before execution begins.

## Replan triggers

Under these conditions the planner is re-invoked:

1. Cumulative graded evidence is below a threshold after the initial DAG completes.
2. Verifier rejects a section and cites "insufficient evidence."
3. User mid-stream asks to expand/narrow scope.

Re-plans inherit prior evidence; the new DAG is a *patch*, not a full replacement.

## Probe fallback (ReAct mode)

When a planned task returns low-quality results (confidence < threshold), the planner emits a **probe task** — a short ReAct-style loop that can adaptively drill into one branch. This preserves plan predictability for 80–90% of traffic while leaving an escape hatch.

## Failure modes

| Mode | Defense |
|---|---|
| Plan over-estimates budget | `estimated_cost_usd` check; user warned; plan can be cut |
| Plan under-specifies queries | Verifier catches; triggers replan |
| Placeholder reference bugs | Schema linter rejects unbound refs at parse time |
| Planner hallucinates a nonexistent tool | `kind` enum strictly validated |

## Metrics

- `planner.tasks_emitted` (distribution)
- `planner.estimated_vs_actual_cost` residuals
- `planner.replan_count`
- `planner.probe_fallback_count`
- `planner.latency_ms` p95
