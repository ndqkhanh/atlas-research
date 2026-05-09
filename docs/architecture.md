# Atlas-Research — Architecture

## What Atlas-Research is

Atlas-Research is a long-horizon autonomous research agent. Given an open-ended research question ("map the state of agentic harness engineering circa April 2026 and produce a publishable-quality report with verified citations"), it produces a structured report with end-to-end faithfulness: every claim cites a source; every source is re-verified during synthesis; the report's structure is auditable against the research trajectory.

Target shape: coverage comparable to OpenAI Deep Research / Gemini Deep Research / Perplexity Pro, with **materially higher faithfulness** (fewer unsupported claims, fewer hallucinated citations) at **bounded cost per report**.

## Honest baselines

| Baseline | Benchmark | Reported result |
|---|---|---|
| OpenAI Deep Research (public) | GAIA (general assistant benchmark) | ~67–72% across tiers as of 2025 leaderboards |
| Gemini Deep Research | BrowseComp (browsing), various internal | similar tier; qualitative |
| Perplexity Pro | BrowseComp, long-form QA | similar tier; strong recall |
| Plain LLM with RAG | GAIA | substantially lower — single-pass retrieval insufficient |

Faithfulness numbers on these products are not systematically public. Reports frequently contain unsupported claims or mis-attributed citations — a widely-acknowledged failure mode.

## Design targets (hypotheses)

- **Faithfulness.** ≥95% of non-trivial claims must have a retrievable, model-verifiable citation. **Assumption:** mandatory cross-channel verification + citation re-check before output.
- **Cost cap.** Fixed max-budget per report (e.g., $3 default, tunable). **Assumption:** ReWOO-style planned parallel retrieval vs. ReAct's open-ended browsing cuts total LLM calls by ~40–60%.
- **Coverage.** Match or exceed Deep Research-class breadth on standard benchmarks. **Assumption:** planner + source router + verifier outperforms monolithic-browsing because of better specialization.
- **Reproducibility.** Same question at time T → substantially overlapping source set (>75% Jaccard) on a second run. **Assumption:** explicit planning + deterministic routing + cache.

These are **targets**, not measurements. Realizing them requires building and evaluating.

## Component diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Atlas-Research Pipeline                          │
│                                                                      │
│    User ──▶ [Intake & Clarify] ──▶ [Query Planner (ReWOO)]           │
│                                         │                            │
│                                         ▼                            │
│                              [Source Router]                         │
│                  ┌──────────────┬──────────────┬─────────────┐       │
│                  ▼              ▼              ▼             ▼       │
│              [Web Search]  [arXiv / papers] [KB / docs]  [your DB]   │
│                                         │                            │
│                                         ▼                            │
│                              [Retrieval Executor]                    │
│                                         │                            │
│                     (parallel fan-out; relevance graded)             │
│                                         │                            │
│                                         ▼                            │
│                             [Synthesis Writer]                       │
│                               │     │     │                          │
│                               ▼     ▼     ▼                          │
│                        sections, citations bound                     │
│                                         │                            │
│                                         ▼                            │
│                            [Citation Verifier]                       │
│                                         │                            │
│                     (every claim ↔ source; re-fetch & check)         │
│                                         │                            │
│                                         ▼                            │
│                              [Report Assembler]                      │
│                                         │                            │
│                                         ▼                            │
│                       [Trace Browser / Report UI]                    │
│                                                                      │
│   ↕  [Memory: prior questions, accepted sources, user preferences]   │
│   ↕  [Cost Router: strong model for plan+verify; cheap for retrieval]│
│   ↕  [Observability: per-source cost, claim coverage, verify rate]   │
└──────────────────────────────────────────────────────────────────────┘
```

## The ten architectural commitments

1. **Intake clarification before planning.** Ambiguous questions get a bounded clarification round with the user (max 3 questions) so the plan is grounded, not guessed. See [blocks/01-intake-clarify.md](blocks/01-intake-clarify.md).
2. **ReWOO-style planned retrieval, not ReAct browsing.** Query Planner emits a DAG of retrievals with placeholders; executor fans out in parallel. See [blocks/02-query-planner.md](blocks/02-query-planner.md).
3. **Source router with specialized surfaces.** Web, arXiv, structured KBs, enterprise DB each route to a purpose-built tool; router picks per query. See [blocks/03-source-router.md](blocks/03-source-router.md).
4. **Relevance grading before synthesis.** Every retrieved chunk passes a grader; irrelevant content is dropped, not "context-for-flavor." See [blocks/04-retrieval-executor.md](blocks/04-retrieval-executor.md).
5. **Subagent pool for deep-dives.** When the planner hits a branch that warrants its own investigation, it spawns a subagent with isolated context and bounded budget. See [blocks/05-subagent-pool.md](blocks/05-subagent-pool.md).
6. **Strict citation binding.** Synthesis cannot emit a claim without a source handle; the binding is structural, not prose. See [blocks/06-synthesis-writer.md](blocks/06-synthesis-writer.md).
7. **Mandatory citation verifier.** Before the report is returned, every binding is re-verified: source still exists, quoted content is still present, attribution is correct. See [blocks/07-citation-verifier.md](blocks/07-citation-verifier.md).
8. **Memory of accepted sources and prior questions.** Future questions benefit from prior high-quality sources; user preferences on depth/style persist. See [blocks/08-memory-citations.md](blocks/08-memory-citations.md).
9. **Cost routing across models.** Strong model on planner and verifier; cheap model on retrieval-side summarization and drafting. Fixed budget. See [blocks/09-cost-routing.md](blocks/09-cost-routing.md).
10. **Trace-browser UI for every report.** User can click any claim and jump to the source + trace step that produced it. See [blocks/10-trace-browser-ui.md](blocks/10-trace-browser-ui.md).

## Data flow for a typical report

1. User question → Intake ensures scope (breadth vs depth, desired length, audience).
2. Query Planner emits a DAG of ~5–20 retrieval tasks.
3. Source Router dispatches each to web / arXiv / KB / private DB.
4. Retrieval Executor runs them in parallel; each result is graded for relevance.
5. Graded evidence is passed to Synthesis Writer, which drafts the report section by section, binding claims to evidence handles.
6. Citation Verifier walks the draft; for each claim, re-fetches the cited source (cached if recent) and checks the support.
7. On verifier pass: Report Assembler produces final markdown + JSON trace.
8. On verifier reject: Synthesis re-drafts the offending section with additional retrieval if needed.
9. User sees the final report + a trace browser for drill-down.

## What distinguishes Atlas-Research

- **Faithfulness as gate, not aspiration.** No report leaves without citation verification.
- **Planned retrieval.** Budget-predictable because the plan is finite; unlike open-ended browsing agents that can spend arbitrarily.
- **Router over sources, not search-only.** Uses arXiv, GitHub, enterprise KBs with appropriate tools, not just web search.
- **Cross-channel evidence per claim.** Where the source has both a primary document and a metadata record (DOI, title), both must agree.

## Non-goals

- Not a chat agent — one question in, one report out.
- Not a code-writing agent — for that, see [Orion-Code](../orion-code/architecture.md).
- Not a real-time decision system — reports can take minutes.
- Not replacing human judgment on contested topics — it cites; users adjudicate.

## Cross-references

- Trade-offs and rejected alternatives: [architecture-tradeoff.md](architecture-tradeoff.md).
- Interfaces, schemas, deployment: [system-design.md](system-design.md).
- Individual components: [`blocks/`](blocks/).
- Underlying techniques: [`research/harness-engineering/`](../../research/harness-engineering/README.md), especially [ReWOO](../../research/harness-engineering/17-rewoo.md), [Agentic RAG](../../research/harness-engineering/25-agentic-rag.md), [Chain-of-Verification](../../research/harness-engineering/18-chain-of-verification-self-refine.md).

## Status

Design specification, April 2026. Not yet implemented.
