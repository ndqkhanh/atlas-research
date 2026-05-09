# Atlas-Research — System Design

## Topology

Atlas-Research deploys as a small service (not a local daemon per-user like Orion-Code) because it scales retrieval better when many users share cache and source indices.

```
                          Browser / CLI
                              │
                              ▼
                      ┌────────────┐
                      │  Gateway   │
                      └─────┬──────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       ┌──────────────┐          ┌───────────────┐
       │  Orchestrator│          │  Cost Router  │
       └──┬─────────┬─┘          └───────┬───────┘
          │         │                    │
          ▼         ▼                    │
     Planner    Verifier                 │
          │         │                    │
          ▼         ▼                    ▼
    ┌───────────────────────────────────────────┐
    │        Retrieval Executor Pool            │
    │   ┌─────────┐ ┌──────────┐ ┌──────────┐   │
    │   │Web MCP  │ │arXiv MCP │ │ KB MCP   │   │
    │   └─────────┘ └──────────┘ └──────────┘   │
    └───────────────────────────────────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │  Cache +     │
                   │  Memory      │
                   └──────────────┘
```

Everything is horizontally scalable except the per-user memory shard.

## Data model

```python
class ResearchRequest:
    id: UUID
    user: UUID
    question: str
    constraints: ReportConstraints  # length, audience, deadline, style

class ReportConstraints:
    max_cost_usd: float = 3.0
    max_wall_clock_s: int = 600
    target_length_words: int = 2500
    audience: Literal["technical", "executive", "academic"] = "technical"
    style: Literal["terse", "standard", "exhaustive"] = "standard"

class QueryPlan:
    request_id: UUID
    tasks: list[QueryTask]        # DAG via `depends_on`
    estimated_cost_usd: float

class QueryTask:
    id: str          # e.g., "#E1"
    kind: Literal["search", "fetch", "fetch_paper", "query_kb", "query_db", "probe"]
    args: dict
    depends_on: list[str]
    source_hint: str | None

class Evidence:
    id: UUID
    query_task_id: str
    source: SourceRef           # URL, DOI, arXiv ID, KB path
    retrieved_at: datetime
    content: str                # normalized text chunk
    relevance_score: float
    status: Literal["graded", "rejected"]

class Claim:
    id: UUID
    text: str
    section_id: str
    evidence_ids: list[UUID]    # mandatory, non-empty
    verified: bool              # set by Citation Verifier
    verification_note: str | None

class Report:
    request_id: UUID
    sections: list[Section]
    references: list[SourceRef]
    trace_id: UUID
    cost_usd: float
    wall_clock_s: float
```

Storage: the canonical artifact is `Report` + its `Claim`s + `Evidence`s, stored with hash-addressed content for reproducibility.

## Public API

### Request a report

```
POST /v1/reports
{
  "question": "...",
  "constraints": { ... }
}
→ 202 Accepted
Location: /v1/reports/{id}
```

### Poll / stream

```
GET /v1/reports/{id}
→ {
  "status": "clarifying" | "planning" | "retrieving" | "synthesizing" | "verifying" | "done" | "failed",
  "progress": { sections_complete: 3, sections_total: 5 },
  "cost_usd_so_far": 1.42,
  "trace_url": "..."
}
```

Server-Sent Events available for live progress.

### Fetch the finished report

```
GET /v1/reports/{id}/markdown   → full text
GET /v1/reports/{id}/json       → structured (Report + Claims + Evidence)
GET /v1/reports/{id}/trace      → full trace for UI
```

### Respond to clarifying questions (if any)

```
POST /v1/reports/{id}/clarify
{ "answers": ["...", "...", "..."] }
```

## Retrieval source interfaces (MCP)

Every source is an MCP server so the retrieval executor is transport-agnostic:

```
tool: web_search(query, k=10, timeframe=None)
  returns: [{url, title, snippet, published_at}]

tool: fetch_url(url, format="markdown")
  returns: {url, title, content, published_at, metadata}

tool: arxiv_search(query, max_results=20)
  returns: [{arxiv_id, title, abstract, authors, date}]

tool: arxiv_get(arxiv_id, sections="all")
  returns: {arxiv_id, title, abstract, body_sections, references}

tool: kb_query(corpus, query, k=10)
  returns: [{kb_id, path, snippet, last_modified}]

tool: db_query(sql, max_rows=1000)
  returns: {columns, rows, query_id}
```

MCP servers for each are pluggable per deployment.

## Cost model

Per-report budget is enforced through a cost router that tracks spend against the ceiling:

```
Planner:    strong model (Opus or o-class)    — 1–2 calls per report
Verifier:   strong model                       — 1 call per ~5 claims
Grader:     cheap model                        — 1 call per retrieval chunk
Drafter:    cheap→medium model                 — 1 call per section + refinements
Summarizer: cheap model                        — 1 per large fetched document
Subagent:   medium model                       — bounded per-subagent budget
```

Typical 2500-word report: ~15–25 LLM calls, ~300–600k tokens total, ~$1.50–$3.00 at April 2026 prices.

## Deployment

- **Service:** containerized (Docker / k8s); stateless workers.
- **State stores:** Postgres (request/report metadata), object store (artifacts + trace), vector store (cache of embeddings, per-user memory), Redis (active-request state).
- **Per-user memory shard:** sharded by user ID; off-the-shelf vector DB (pgvector works).
- **Observability:** OTel traces, Prometheus metrics, Langfuse for LLM call inspection.
- **Secrets:** per-tenant scoped; MCP server credentials mount per-connection.

## SLOs

| Metric | Target |
|---|---|
| Time to first section | p50 < 90s, p95 < 180s |
| Report completion | p50 < 4 min, p95 < 9 min |
| Cost per report | p50 ≤ $2.00, p95 ≤ $3.00 |
| Citation verification pass rate on first draft | ≥ 90% |
| Faithfulness (claims with valid citation) | ≥ 95% |
| Cache hit rate on source fetches within 24h | ≥ 60% |

## Failure handling

| Failure | Response |
|---|---|
| Source tool unavailable | Router retries with alternate source; final report notes the gap |
| Retrieval DAG returns no evidence on branch | Planner re-plans the branch once; then surfaces as "insufficient evidence" |
| Citation verifier rejects | Synthesis re-writes the offending section; if rejected again → `verifier_stalemate` (flagged) |
| Cost cap imminent | Planner may cut optional sections; user is warned |
| User doesn't answer clarify | After timeout, proceed with best-guess intake and flag ambiguity |
| Rate-limited upstream LLM | Backoff + queue; cost router may switch provider |

## Security & privacy

- **Enterprise connectors** authenticate per-request with user's own scopes — Atlas never stores customer data server-side beyond the per-user memory, and that's opt-in.
- **Source proxy isolation** — each MCP server runs sandboxed.
- **Supply-chain defense** — following arXiv:2604.08407, no untrusted third-party LLM routers; direct vendor endpoints with request signing where available.
- **Prompt-injection hygiene** — all fetched content is wrapped in UNTRUSTED markers (see [Orion-Code block 05](../orion-code/blocks/05-tool-layer.md)).
- **Right to erasure** — per-user memory deletable; all artifacts referencing a user purgeable by user ID.

## Roadmap (post-v1)

- **Cross-report synthesis.** Meta-reports that analyze trends across prior reports.
- **Active learning loop.** User feedback on cited sources improves source rating over time.
- **Domain packs.** Pre-configured source routers + rubrics for biomed, legal, finance.
- **Collaboration.** Multi-user reports with review rounds.
- **Integrated fact-check feedback.** Let users flag a claim as wrong and re-route.

## Anti-scope

- No code writing → Orion-Code.
- No production mutation → Aegis-Ops.
- No voice interaction → Harmony-Voice.
- No multi-tenant agent orchestration product → Syndicate.
