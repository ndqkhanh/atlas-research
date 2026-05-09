# Atlas-Research Block 06 — Synthesis Writer

## Responsibility

Produce the report's prose, section by section, with every claim **structurally bound** to one or more `Evidence` IDs. Never emits free-form text without a binding.

## Inputs

- Research Brief.
- Graded `Evidence` set grouped by query task.
- Subagent findings (with sources attached).
- Style / audience / length from constraints.

## Output

- A `Report` object with ordered `Section`s.
- Each paragraph may contain multiple `Claim`s; each `Claim` has `evidence_ids`.

## Workflow

1. **Outline.** The writer first proposes a report outline: sections and, for each, the expected evidence groups. One strong-model call.
2. **Section drafting.** For each section, the writer drafts prose in "claim-with-evidence" form. A medium-model call per section (cheaper than one monolithic call, and parallelizable).
3. **Transitions & flow pass.** A final pass polishes connectives and ensures consistent terminology. Shortest call; cheap model.
4. **Reference list.** Assembled from the evidence sources.

## Structural binding

Internal prose format (pre-render):

```
{{claim: evidence_ids=[e17, e22]}}
Modern harnesses separate the reasoning loop from infrastructure concerns
via a gateway-plus-plugin architecture.
{{/claim}}
```

Rendered markdown:

```markdown
Modern harnesses separate the reasoning loop from infrastructure concerns
via a gateway-plus-plugin architecture [17], [22].
```

Every `[N]` in the rendered output resolves to a source in the reference list, and the link goes through the trace browser so users can jump to the exact retrieved chunk.

## Anti-hallucination disciplines

- **No evidence → no claim.** The writer's system prompt forbids emitting a claim without a non-empty `evidence_ids` list. A validator at render time rejects any claim without bindings.
- **Direct quotes must be exact.** Quoted text is compared (string-match or high-similarity) to the cited chunk; mismatches reject.
- **Numbers must be traceable.** "23% undetected sabotage rate" must appear in or be a direct reformulation of a cited chunk; the verifier checks.

## Section templates (seed, adapted by brief)

- Research survey: intro / landscape / key-techniques / open-problems / references.
- Comparative: intro / dimensions / per-item-analysis / synthesis / recommendation / references.
- Status-of-X: intro / background / current-state / debates / outlook / references.

The writer may deviate with justification; the outline step locks in the final structure.

## Style controls

- `terse` — short sentences, bullets preferred, minimal hedging.
- `standard` — conventional prose, balanced.
- `exhaustive` — longer explanations, more qualifications.

Style is a prompt-level knob; evaluator scores include a style-adherence criterion.

## Failure modes

| Mode | Defense |
|---|---|
| Free-form prose without evidence | Structural validator at render time |
| Hallucinated quote | String-match check |
| Numbers invented | Verifier's fact-check path |
| Section bloat (padding) | Length cap per section, derived from overall length target |
| Inconsistent terminology | Flow pass enforces a glossary built from the brief |

## Metrics

- `synthesis.sections_drafted`
- `synthesis.tokens_by_section`
- `synthesis.validator_rejects` (pre-render)
- `synthesis.style_score` (from evaluator rubric)
- `synthesis.cost_usd` per section
