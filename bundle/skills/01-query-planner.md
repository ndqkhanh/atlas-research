---
name: query-planner
description: Decompose a research question into 5-10 typed sub-queries.
---
# Query Planner

Take the user's research question. Decompose into sub-queries:

```yaml
sub_queries:
  - query: <text>
    evidence_type: paper | dataset | blog | primary | docs
    priority: 1-5         # 1 highest
    expected_specificity: low | medium | high
```

5–10 sub-queries is the sweet spot. Fewer = poor coverage; more =
diluted attention. Reorder by priority before execution.

The planner is **deterministic** for a given question + plan
template, so re-runs reproduce — important for eval reproducibility.
