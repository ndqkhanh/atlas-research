# Atlas-Research Block 04 — Retrieval Executor

## Responsibility

Execute the `QueryPlan`'s DAG, respecting dependencies and parallelism caps. Grade every retrieved chunk for relevance. Emit `Evidence` records downstream.

## Execution model

1. Topological sort of tasks by `depends_on`.
2. For each ready task (no pending deps), dispatch via the Source Router.
3. Up to `max_parallel` tasks run concurrently (default 6).
4. As results arrive, resolve downstream placeholders (`{#E1[0].url}`).
5. Completed results go through the grader → Evidence store.

Pseudo-code:

```python
async def execute(plan):
    ready = [t for t in plan.tasks if not t.depends_on]
    futures = {t.id: schedule(t) for t in ready}
    results = {}
    while futures:
        done = await wait_first(futures.values())
        for t_id, fut in list(futures.items()):
            if fut.done():
                results[t_id] = fut.result()
                del futures[t_id]
                # newly-ready?
                for nxt in plan.tasks:
                    if nxt.id not in results and nxt.id not in futures:
                        if all(d in results for d in nxt.depends_on):
                            resolved = resolve_placeholders(nxt, results)
                            futures[nxt.id] = schedule(resolved)
    return results
```

## Relevance grading

Every retrieved chunk (web page section, paper abstract, KB doc) is graded by a cheap LLM pass:

```
prompt:
  Given the research brief and this chunk, score 0–1 on:
  - relevance (matches the brief's scope)
  - authoritativeness (source trust × author/venue reputation)
  - freshness (within requested time window)
  Return JSON with scores and 1-sentence rationale.
```

Chunks with `relevance < 0.3` are dropped; chunks with `relevance < 0.6` are kept only if other evidence for that task is thin.

## Chunking strategy

- **Web pages:** split on headings, max 800 tokens per chunk, with title + URL attached.
- **Papers (arXiv):** abstract + intro + selected sections (by heading match against the brief) + references that match prior queries.
- **KB docs:** chunk on section boundaries; preserve metadata (path, last-modified).
- **DB rows:** serialize as table snippet; cap at ~50 rows/chunk.

Chunks carry a `SourceRef`: URL + offset/heading + hash. Hash is the citation-verification anchor later.

## Deduplication

- Exact content hash match → drop duplicates.
- High-similarity chunks (cosine >0.95 on a small embedder) → keep the highest-ranked one by `relevance × authoritativeness`.

## Caching

Source fetches cache by URL + hash + `retrieved_at`. TTL per source:

- arXiv abstracts: 7 days.
- Web pages: 24 hours (news-sensitive lower).
- KB docs: respect `last_modified` (invalidate on change).

Cache dramatically lowers cost on related reports within the TTL window.

## Failure handling

| Failure | Response |
|---|---|
| Source times out | Retry once; then mark task as failed, continue DAG |
| All retrievals in a branch low-relevance | Branch-level `evidence_thin` flag; planner may replan |
| Rate limit | Backoff; may route to alternate provider |
| Chunking fails (mangled PDF) | Fallback to abstract-only; verifier warned |

## Budget enforcement

Executor tracks per-report spend:

- Before each dispatch, check remaining budget vs estimated cost.
- If remaining budget drops below threshold, planner is signalled to cut optional branches.

## Failure modes and defenses

- **Tool output injection** → every fetched content wrapped in UNTRUSTED markers; grader instructions insulated.
- **Paywalled content** → source tool returns abstract + paywall flag; verifier knows to require abstract-only support.
- **Outdated cache** → TTLs; manual purge for critical domains.
- **Biased relevance grading** → periodic human relabel; recalibration when κ drops.

## Metrics

- `retrieval.tasks_dispatched`, `retrieval.tasks_succeeded`
- `retrieval.parallelism_gauge`
- `retrieval.cache_hit_rate` by source
- `grader.mean_relevance` by source
- `evidence.rejected_by_grader_count`
- `retrieval.cost_usd` per report
