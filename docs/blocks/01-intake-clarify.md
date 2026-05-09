# Atlas-Research Block 01 — Intake & Clarify

## Responsibility

Convert an ambiguous user question into a scoped, answerable research brief before any planning cost is spent. Bounded by a max of 3 clarifying questions to respect the user's time.

## Inputs & outputs

- **Input:** raw question string + `ReportConstraints` (cost cap, target length, audience, style).
- **Output:** a **Research Brief** — scoped question, explicit assumptions, user preferences, and (optionally) a list of sub-questions.

## Workflow

1. **Classify ambiguity.** A classifier LLM call identifies ambiguity dimensions:
   - Scope breadth — "map the state of agentic AI" is vast; "map the state of harness engineering for coding agents Q1 2026" is tractable.
   - Audience — technical vs executive.
   - Time window — "recent" needs a date.
   - Success criterion — taxonomy vs survey vs compare-N approaches.
2. **Ask up to 3 questions.** Using the AskUserQuestion-style protocol (multi-choice + free-text "other"). No more than 3, because >3 feels interrogative.
3. **Bake user answers into the brief.** The brief is short (under 200 words) and becomes part of the planner's system prompt.

## Brief template

```markdown
# Research Brief

## Question (scoped)
<single-sentence version>

## Scope
- in: [...]
- out: [...]

## Audience & style
<e.g., "technical engineers; terse; code-forward examples">

## Success criterion
<what the report must contain to be considered "done">

## Open assumptions
- <things the agent is assuming because user didn't specify>

## User preferences applied
- (from memory) prefers bullet summaries
- (from memory) cites arXiv IDs not DOIs
```

## When clarify is skipped

- Explicit `--no-clarify` flag (user accepts guessed scope).
- Question matches a prior question closely (memory-match >0.9 embedding similarity); the prior brief is proposed and user confirms.
- User provides a scoped question with explicit scope/audience/style already (skip detection via heuristic).

## Failure modes

- **Runaway clarification.** Hard cap of 3 rounds, then proceed.
- **Low-quality brief.** Planner can send back a "brief-too-ambiguous" signal; intake gets one more chance.
- **User over-specifies.** Brief contains more constraints than the question supports; planner flags "constraint conflict."

## Metrics

- `intake.clarify_rounds` (distribution)
- `intake.skipped_count`
- `brief.revision_count` (when planner rejects and asks for re-intake)
