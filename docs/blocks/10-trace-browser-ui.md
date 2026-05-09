# Atlas-Research Block 10 — Trace Browser UI

## Responsibility

Make the research trajectory inspectable. For every claim in the report, the user can jump to the source; for every source, to the retrieval trace; for every retrieval, to the planner task that requested it. The UI is a consumer of the JSON trace artifact the rest of the pipeline emits.

## Target experience

The reader has three lenses:

1. **Report view.** The markdown report with citations rendered as links.
2. **Claim view.** Click a citation → side panel opens with the cited chunk, its source, and the retrieval that produced it.
3. **Trace view.** Full end-to-end trajectory: brief → plan → retrievals → graded evidence → synthesis → verification. Collapsible, filterable, searchable.

## Data model the UI consumes

The report bundle:

```
report.json         # Report + Claim + Evidence, denormalized for UI
sources/*.json      # per-source metadata + cached content
trace.jsonl         # ordered spans from the pipeline
rubric.json         # evaluator scores per section
verification.json   # faithfulness report
```

All IDs are stable and cross-referenced so a single click resolves across views.

## Key interactions

- **Follow a citation.** `[17]` in prose → source panel with title, URL, retrieved-at, chunk highlight of the supporting text.
- **"Where did this claim come from?"** → scroll the trace to the graded Evidence that produced it; each hop up is one parent task.
- **"Why did the verifier reject?"** → dedicated verification view: rejected claims with reasons; can request re-draft.
- **Source trust signals.** Per-source trust tier badge (authoritative / credible / general) with hover explaining.
- **Cost & cadence.** A small sparkline of spend over time per section + per source.

## Annotations & feedback

User can annotate claims:
- "This is wrong" (feeds back to memory; source's trust drops).
- "This is exactly right" (source's trust rises).
- "Missing something" (spawns a follow-up subagent if budget allows).

Feedback is stored per-user; optionally rolled up anonymously for the citation store.

## Accessibility and export

- Report is exportable as Markdown, PDF, HTML, or JSON-LD.
- Keyboard-navigable (tab through claims; Enter opens source).
- Screen-reader friendly (semantic HTML; ARIA labels on panels).
- Offline viewable (the bundle is self-contained, no live-fetch needed).

## Embed mode

For use inside enterprise systems (Confluence, Notion, internal docs):

- iframe-embed of the report with citations clickable.
- JSON export for downstream tooling.
- Per-claim API: `GET /v1/reports/{id}/claims/{claim_id}` returns its verifier status + evidence, so third-party tooling can audit.

## Performance

- Initial render: <500ms for reports under 5k words.
- Trace view lazy-loads; typical trace has 200–2000 spans.
- Search across claims: client-side index, <100ms.

## Failure modes

| Mode | Defense |
|---|---|
| Large reports slow the UI | Lazy-load sections; virtualized lists in trace view |
| Broken source link | UI caches fetched chunk; falls back to cache with "original URL" note |
| User abuses feedback (spam) | Rate-limit; moderation on citation-store-wide feedback |
| Export format drift | Canonical markdown; other formats derived |

## Metrics

- UI adoption: % of reports viewed in browser vs downloaded
- Claim-click-through rate (engagement with citations)
- Feedback counts per report
- Export format mix
- UI latency p95
