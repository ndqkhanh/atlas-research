# Atlas-Research Block 09 — Cost Routing

## Responsibility

Route each LLM call to the right model tier (strong / medium / cheap) so the report hits its quality bar under a fixed budget. Enforce the per-report cost cap by throttling or cutting when the budget is close to exhausted.

Reference: [`24-observability-tracing.md`](../../../research/harness-engineering/24-observability-tracing.md) (cost attribution), [`16-plan-and-solve.md`](../../../research/harness-engineering/16-plan-and-solve.md) (strong-planner, cheap-executor pattern).

## Tier table

| Tier | Typical models (April 2026) | $/1M input | $/1M output | Use |
|---|---|---|---|---|
| `strong` | Opus-class, o-reasoning | $15 | $75 | Planner, Verifier, complex synthesis |
| `medium` | Sonnet-class, mid-tier GPT | $3 | $15 | Section drafting, subagent main work |
| `cheap` | Haiku-class, mini-tier GPT | $0.25 | $1.25 | Grading, summarization, classification |
| `nano` | Nano-class | $0.05 | $0.25 | Routing, monitoring, micro-tasks |

Prices are illustrative snapshots; the deployment's price table is updated by the Cost Router at service start and re-evaluated daily.

## Call classification

Every LLM call declares:

```python
model_route.request(
    purpose="plan" | "synthesize" | "draft_section" | "grade" | "verify" | "classify",
    context_tokens_estimate=12000,
    output_tokens_estimate=400,
    importance="high" | "normal" | "low",
)
```

The router picks the tier based on `purpose`, `importance`, and the remaining budget.

Default mapping:

- `plan`, `verify` → strong.
- `synthesize` (outline) → strong.
- `draft_section` → medium.
- `grade`, `classify` → cheap.
- `monitor` (safety / anomaly) → nano.

## Budget tracking

- Running spend maintained per `ResearchRequest`.
- When spend crosses `cost_ceiling × 0.7`, the router enters **preservation mode**: downgrade non-critical calls by one tier, skip optional subagent spawns.
- At `cost_ceiling × 0.9`, the pipeline may cut optional sections (advisory content); planner signals user.
- At `cost_ceiling × 1.0`, hard stop: the partial report is finalized; explicit "budget exhausted" notice added.

## Cache-aware cost

Prompt caching cuts costs significantly on stable prefixes. The Cost Router tracks cache hit rate; a high cache-hit call costs ~10% of the first call. Budget estimates factor this in.

## Provider failover

Each tier has a primary and at least one secondary provider (where contract allows):

```
strong:  [anthropic/opus-4-7, openai/o-class]
medium:  [anthropic/sonnet-4-6, openai/gpt-5-mid]
cheap:   [anthropic/haiku-4-5, openai/gpt-5-mini]
nano:    [anthropic/haiku-nano, openai/gpt-5-nano]
```

On provider outage / rate limit / >2× baseline latency → transparent failover. Failover events logged; cost & latency metrics per provider tracked separately.

## Different-family discipline

For any call pair where "different family" matters (Planner ↔ Verifier, Generator ↔ Evaluator), the router explicitly selects different families. If only one family available, emit a warning span tagged `degraded_eval=same_family`.

## Failure modes

| Mode | Defense |
|---|---|
| Over-downgrade quality hit | Tiering is per-purpose; critical calls stay strong under preservation |
| Provider-pricing drift | Daily re-evaluation of price table |
| Cache miss cliff | Structural discipline on prompt prefixes (see Orion-Code block 04) |
| Budget exhaustion mid-section | Graceful truncation with explicit note |
| Provider outage cascade | Failover list; surfaced in trace |

## Metrics

- `cost.spend_usd_per_report` p50/p95
- `cost.by_tier` distribution
- `cost.cache_hit_rate` per purpose
- `cost.preservation_mode_count`
- `cost.budget_exhaustion_count`
- `cost.provider_failover_count`
- `cost.tier_upgrade_count` (when low-tier call was retried at higher)
