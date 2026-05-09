# Atlas-Research — Long-Horizon Research Agent (MVP)

Walking-skeleton implementation of the [Atlas-Research design](architecture.md). Turns a user question into a structured, citation-verified report via ReWOO-style planned retrieval + synthesis + claim-level verification.

## What works today

- **`QueryPlanner`** — decomposes a question into a small DAG of retrieval tasks (`web_search`, `arxiv_search`, `fetch_url`).
- **`Retriever`** ABC with **`MockRetriever`** — returns deterministic canned evidence; swap in a real MCP search server for production.
- **`SynthesisWriter`** — produces claim-bound report sections (one per source kind).
- **`CitationVerifier`** — every claim must cite existing evidence AND share lexical overlap with it; otherwise rejected.
- **`AtlasPipeline`** — orchestrates all stages with a shared `harness_core.Tracer`.
- **FastAPI HTTP surface** — `POST /v1/reports` returns rendered markdown + faithfulness ratio.
- **MockLLM default** — pipeline is deterministic; tests don't need API keys.

## What is stubbed

- Real LLM-driven planning is replaced by a 3-task deterministic plan (strong enough to exercise the pipeline).
- No web fetcher; `MockRetriever` returns canned content. Plug in a real retriever by subclassing `Retriever` and passing it into `AtlasPipeline(retriever=...)`.
- Synthesis is rule-based (one claim per evidence chunk, summary = first two sentences). Real systems call the LLM here.
- No subagent pool, no cost router, no trace browser UI.

See [architecture.md](architecture.md) for the full design.

## Run locally

From **this project folder** (`atlas-research/`):

```bash
make install      # .venv + harness_core + this project editable
make test         # run tests
make run          # http://localhost:8002/docs
```

Example request:

```bash
curl -s -X POST http://localhost:8002/v1/reports \
  -H 'content-type: application/json' \
  -d '{"question": "What is harness engineering?"}' | jq
```

Returns:

```json
{
  "markdown": "# What is harness engineering?\n\n## Arxiv findings\n- Abstract: we present work on ...",
  "faithfulness_ratio": 1.0,
  "total_claims": 3,
  "verified_claims": 3,
  "cost_usd": 0.15
}
```

## Run via Docker

```bash
make docker-up
curl -s http://localhost:8002/healthz
make docker-down
```

## HTTP API

### `POST /v1/reports`

```json
{
  "question": "required — the research question",
  "audience": "technical" | "executive" | "academic",
  "style":    "terse" | "standard" | "exhaustive",
  "max_cost_usd": 3.0,
  "target_length_words": 2500
}
```

Returns:

```json
{
  "markdown": "...rendered report...",
  "faithfulness_ratio": 0.92,
  "total_claims": 12,
  "verified_claims": 11,
  "cost_usd": 0.20
}
```

### `GET /healthz`

Returns `{"status": "ok", "service": "atlas-research"}`.

## Python API

```python
from atlas_research import AtlasPipeline, Brief

pipeline = AtlasPipeline()
result = pipeline.run(Brief(question="What is harness engineering?"))

print(result.report.to_markdown())
print(f"faithfulness: {result.verification.faithfulness_ratio:.0%}")
```

Swap the retriever:

```python
from atlas_research import AtlasPipeline, MockRetriever, Evidence, SourceRef

retriever = MockRetriever(canned_evidence=[
    Evidence(
        source=SourceRef(kind="arxiv", identifier="arxiv:2604.15034", title="Autogenesis"),
        content="Autogenesis is a self-evolving agent protocol...",
    ),
])
pipeline = AtlasPipeline(retriever=retriever)
```

## Tests

```bash
make test
```

Suite:
- [`tests/test_pipeline.py`](tests/test_pipeline.py) — planner / retriever / synthesizer / verifier unit tests + full pipeline E2E.
- [`tests/test_app.py`](tests/test_app.py) — FastAPI endpoints.

## Architecture mapping

| Block | Code |
|---|---|
| [01 Intake Clarify](blocks/01-intake-clarify.md) | **TODO v0.2** — currently a pass-through |
| [02 Query Planner](blocks/02-query-planner.md) | `atlas_research.planner.QueryPlanner` |
| [03 Source Router](blocks/03-source-router.md) | `atlas_research.retriever.Retriever` (one subclass per source) |
| [04 Retrieval Executor](blocks/04-retrieval-executor.md) | `atlas_research.retriever.MockRetriever` (MVP) |
| [06 Synthesis Writer](blocks/06-synthesis-writer.md) | `atlas_research.synthesizer.SynthesisWriter` |
| [07 Citation Verifier](blocks/07-citation-verifier.md) | `atlas_research.verifier.CitationVerifier` |

## Production readiness

- [x] Structured data model (pydantic)
- [x] Claim-evidence binding required; unverified claims flagged
- [x] Deterministic tests with mock retriever
- [x] FastAPI with healthcheck
- [x] Dockerfile
- [ ] Real LLM-driven planner + synthesizer (MVP uses deterministic rules)
- [ ] Real web retriever (MVP ships MockRetriever)
- [ ] Trace browser UI
- [ ] Subagent pool for deep-dives

## License

MIT

## TUI

A polished terminal interface ships out of the box, powered by the shared
[`harness-tui`](../../packages/harness-tui) package.

```bash
make install     # installs harness-tui editable alongside this project
make tui         # opens the TUI against the running FastAPI backend
make tui-mock    # demo: scripted events, no backend needed
```

Features:

- **Brand theme** with project ASCII logo + spinner pack.
- **Hero sidebar widget**: Live citations panel with source detail.
- 16 built-in slash commands: `/help`, `/plan`, `/why`, `/cost`, `/recipe`,
  `/test`, `/find`, `/voice`, `/theme`, `/resume`, `/clear`, `/auto`,
  `/default`, `/quit`, `/cost tool`, `/cost agent`.
- Differentiators built in:
  - Stacked context-budget bar (system / files / conversation / output).
  - Latency sparkline with TTFT + inter-token measurements.
  - Per-tool / per-subagent token + cost rollup table.
  - Typed `Plan` editor (reorder + edit before execution).
  - Per-hunk diff approval (`y/n/a/d/q`).
  - Permission gates with blast-radius preview (dry-run output).
  - Auto-test / auto-lint loop (`/test on`).
  - Recipes (Goose-style YAML) under `recipes/`.
  - Transcript search (`Ctrl+F`).
  - Dual-cursor composer (input + agent quick-replies).
  - Voice mode (`F9` push-to-talk; `pip install 'harness-tui[voice]'`).
  - Web mode (`--serve` via `textual-serve`).
  - SSH mode (`--ssh` via `asyncssh`).
- **Visual snapshot tests** in CI — every PR diffs the SVG-rendered TUI.

See [`research/tui-state-of-the-art.md`](../../research/tui-state-of-the-art.md)
and [`research/tui-framework-and-rollout.md`](../../research/tui-framework-and-rollout.md)
for the design.
