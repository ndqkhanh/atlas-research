# Atlas-Research Block 03 — Source Router

## Responsibility

Decide which tool/surface each `QueryTask` should go to, based on the task's `kind`, `source_hint`, and the deployment's source registry. Provides a uniform tool interface to the executor so new sources can be added without changing the executor.

## Source registry

Every deployment has a `sources.yaml`:

```yaml
sources:
  web:
    tool: "mcp__web__search"          # or exa, brave, you.com
    cost_per_call_usd: 0.005
    latency_ms_p50: 400
    score_domains:                    # hints the planner considers
      preferred: ["arxiv.org", "docs.anthropic.com", "openai.com",
                   "research.google", "github.com"]
      demoted: ["pinterest.com", "quora.com"]
  arxiv:
    tool: "mcp__arxiv__search"
    cost_per_call_usd: 0.000
    latency_ms_p50: 300
  internal_kb:
    tool: "mcp__corporate_kb__query"
    cost_per_call_usd: 0.000
    requires_auth: true
  postgres_analytics:
    tool: "mcp__pg_analytics__query"
    schema: "read_only_reports"
  github:
    tool: "mcp__github__search_code"
    cost_per_call_usd: 0.000
```

The router consults this registry when binding `QueryTask.kind` to a concrete tool call.

## Routing rules (in order)

1. If `source_hint` is set, try that source first.
2. Match `kind` to the registry (e.g., `arxiv_search` → `arxiv` source).
3. If multiple sources match (e.g., `fetch_url` could be generic web fetch or a domain-specialized fetcher), prefer:
   - Explicit domain match (arxiv.org → arxiv fetcher; docs.*.com → doc-aware fetcher).
   - Lowest `cost_per_call_usd`.
   - Lowest `latency_ms_p50`.
4. Fall back to web if no specialized source applies.

## Router-injected augmentations

The router can transparently augment queries based on source:

- **arXiv:** strip Google-query decorations ("site:", "filetype:") the search engines understand but arXiv doesn't.
- **Web search:** apply date filters from the brief's time window.
- **GitHub code search:** rewrite natural-language to code-oriented (`"ReWOO implementation"` → `path:**/rewoo* language:python`).

Augmentations are conservative and logged so the user can see what the router did.

## Per-source safety

Each source carries safety metadata:

- **Trust tier:** `authoritative` (arXiv, vendor docs) / `credible` (major publications) / `general` (open web).
- Evidence from lower-trust sources gets lower relevance scores in the executor; verifier requires authoritative sources for load-bearing claims.

## Enterprise connector protocol

Enterprise KB / DB connectors are MCP servers; the router knows only:

- Tool name + args.
- Scope: which corpora / which tables are queryable for this request's authenticated user.
- Trust tier.

The connector's internals (auth, tenant isolation, query planning within the KB) are opaque to the router.

## Failure modes

| Mode | Defense |
|---|---|
| Source unavailable | Fallback to next-best per registry; report notes missing source |
| Domain-inflated rank from a specialized source | Cross-check against web search for anomalies |
| Routing causing cost spike | Registry's `cost_per_call_usd` informs the planner's estimate |
| Query rewriting mangles intent | Rewrites logged; verifier can trigger un-rewritten retry |

## Metrics

- `router.decisions_by_source`
- `router.rewrite_count`
- `router.fallback_count`
- `source.availability_gauge`
- `source.cost_per_call_actual` vs. registered
