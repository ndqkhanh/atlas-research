# Atlas-Research — Architecture Trade-offs

## Trade-off 1: ReWOO-style planned retrieval vs ReAct-style interactive browsing

**Chosen:** Planned retrieval via DAG of queries with placeholders. Executor fans out in parallel.

**Alternative:** ReAct-style browsing — model sees one page, decides next query, repeats.

**Why planned:** Cost predictability and parallelism. ReAct-style agents can run for arbitrary time; planned retrieval has a finite DAG you can budget. Parallelism roughly halves wall-clock.

**Cost:** Plans from bad initial understanding produce poor retrievals. Mitigated by the **Intake Clarify** stage and by a **replan-on-insufficient-evidence** path in the Retrieval Executor.

**Fallback:** ReAct-style probe when the planner has low confidence — emit a "probe" subtask that can adapt mid-stream.

## Trade-off 2: Mandatory citation verification vs trust-the-draft

**Chosen:** Verifier re-fetches every cited source and checks support before returning the report.

**Alternative:** Trust synthesis output; add verifier only on request.

**Why:** Faithfulness is the headline differentiator. Public Deep Research products produce many unsupported claims; Atlas's value proposition is that reports do not.

**Cost:** ~20–30% additional latency and token spend. Mitigated by source-side caching and by batching verification.

## Trade-off 3: Source router with multiple tools vs search-only

**Chosen:** Explicit router across web, arXiv, enterprise KB, structured DB.

**Alternative:** Unified web search that indirectly covers papers/KBs.

**Why:** Specialized surfaces provide structured metadata (DOIs, abstracts, authorship) web search strips. Citation verification is cheaper when the source has structured IDs.

**Cost:** Multiple tool integrations to maintain. Mitigated by MCP — arXiv, GitHub, enterprise DB plug in as servers.

## Trade-off 4: Subagent pool for deep-dives vs flat planning

**Chosen:** Planner can spawn subagents for sub-questions that warrant their own investigation.

**Alternative:** Single flat planning pass.

**Why:** Some sub-questions become their own mini-research projects. Spawning a subagent with isolated context keeps the main synthesis lean; the subagent returns a structured summary with its own sources.

**Cost:** Orchestration complexity; risk of subagent over-spawning. Mitigated by budget caps and depth caps (no sub-subagents in v1).

## Trade-off 5: Same-family vs different-family verifier

**Chosen:** Different-family verifier preferred; fallback to same-family with warning.

**Why:** Same as [Orion-Code 's trade-off 5](../orion-code/architecture-tradeoff.md). Shared-blind-spot bias is the main failure mode of self-verification.

**Cost:** Two vendor relationships.

## Trade-off 6: Fixed cost cap vs cost-free "research until done"

**Chosen:** Fixed per-report budget (default $3, user-configurable).

**Alternative:** Open-ended "keep researching until confident."

**Why:** Predictability; users value knowing cost upfront. Also: budget caps prevent runaway loops.

**Cost:** On under-planned reports, the budget may exhaust before the full question is covered. Mitigated by the planner warning in advance if a plan's estimated cost exceeds the cap.

## Trade-off 7: Markdown + JSON trace output vs rich web UI only

**Chosen:** Report is markdown (universal, version-controllable, email-able) + a JSON trace (for the browser UI).

**Alternative:** Proprietary web-only format.

**Why:** Markdown is universal; JSON trace is machine-processable; no lock-in. UI is a consumer of both.

**Cost:** More output formats to test. Mitigated by treating markdown as canonical and UI as derived.

## Trade-off 8: Memory of accepted sources vs cold-start every report

**Chosen:** Memory persists across reports: source quality ratings, user style preferences, prior questions.

**Alternative:** Cold-start every report (simpler, more private).

**Why:** A researcher who accepted a source once should not re-verify it from scratch next time. User feedback on style (terse vs. verbose) persists.

**Cost:** Memory management overhead; privacy surface. Mitigated by explicit per-user memory scope and GDPR-style erasure.

## Trade-off 9: Hierarchical decomposition vs flat question → answer

**Chosen:** Reports have enforced structure (intro / sections / synthesis / open questions / references) with per-section retrieval plans.

**Alternative:** Free-form single-pass answer.

**Why:** Structure improves readability; sectioning lets the verifier work incrementally; plan-per-section keeps the context lean.

**Cost:** Rigidity — some questions don't want sections. Mitigated by letting the Planner propose a flat structure when appropriate.

## Trade-off 10: Enterprise DB connector vs public-only retrieval

**Chosen:** Enterprise connector is a first-class source via MCP (user can mount their own KBs, wikis, DBs).

**Alternative:** Public data only (simpler, fewer integrations).

**Why:** Most valuable research questions inside an organization involve private context. Treating enterprise data as a first-class source, with its own retrieval / verification patterns, is the differentiator.

**Cost:** Authentication, authorization, data-handling complexity. Mitigated by delegating to MCP: the server handles the integration; Atlas handles the routing.

## Rejected alternatives

### Fine-tune a research-specialist model
Rejected for v1. Frontier models + a strong harness cover most of the gap; specialization can come later if data justifies. The [Adaptation Survey](../../research/harness-engineering/47-adaptation-of-agentic-ai-survey.md) A1 paradigm is a v2 option.

### Real-time streaming output as it's retrieved
Rejected. Streaming partial claims without verification defeats faithfulness. Users see progress (sections completing) but claims land only post-verification.

### One monolithic LLM call with huge context
Rejected. Context rot (Chroma 2025) kills quality; also no per-claim auditability.

### Public-only benchmark-chasing
Rejected. GAIA and BrowseComp are useful anchors but Atlas is a product, not a leaderboard entry. Some design choices (citation verifier, cost cap) hurt leaderboard numbers and help real users; we pick users.

### User-facing agent chat inside the report UI
Rejected for v1. Reports are artifacts; follow-up questions spawn new reports with prior context. Avoids the "agent loops on follow-ups" failure class.

## What breaks outside design envelope

- **Live-news questions.** Atlas is calibrated for research with verifiable sources; breaking-news questions need different trust tiers (primary reporting is often wrong initially). Atlas will decline or warn.
- **Opinion questions.** "Is X better than Y?" is underspecified; Atlas asks for the evaluation criterion during Intake Clarify.
- **Chat-style follow-ups.** Use the "research from prior" mode; conversation is not supported.
- **Massive corpora that don't fit the retrieval budget.** The cap will be hit; the report will be explicit about coverage gaps.
