# Atlas-Research Block 07 — Citation Verifier

## Responsibility

Before a report is released, check every `Claim`'s bindings: does the cited source still exist? Does the cited content still say what the report says it says? Is the attribution correct (right paper, right section)? Rejects claims that fail.

Reference: [`18-chain-of-verification-self-refine.md`](../../../research/harness-engineering/18-chain-of-verification-self-refine.md), [`25-agentic-rag.md`](../../../research/harness-engineering/25-agentic-rag.md).

## Two-pass verification

### Pass 1 — structural checks (fast)

- Every `Claim` has at least one `evidence_id`.
- Each `evidence_id` resolves to an `Evidence` row whose `SourceRef` still resolves.
- Quoted strings in the claim (if any) string-match the cited chunk.
- Numbers in the claim (if any) appear in the chunk (direct match or simple reformulation).

Fail any → reject the claim with a specific reason.

### Pass 2 — semantic verification (LLM, different-family)

For each claim that passed Pass 1:

```
Prompt:
Given the claim:
  "<claim text>"
And the cited evidence:
  <evidence chunk(s)>
Decide: does the evidence support the claim? Return JSON:
  { "supported": true|false,
    "reason": "<1 sentence>",
    "confidence": 0-1 }
Only answer based on the evidence given; do not use world knowledge.
```

Claims failing this pass are rejected with the reason attached.

## Re-fetch for freshness

For Evidence fetched >24h ago (or whose source has a shorter TTL), the verifier re-fetches. Changes:

- Source no longer resolves → claim rejected.
- Source content changed materially → relevance re-graded; if unsupported after change, rejected.
- Source unchanged → proceed.

## Rejection handling

Rejected claims are sent back to the [Synthesis Writer](06-synthesis-writer.md) with the reject reason. The writer has three options:

1. **Strengthen.** Re-draft with additional evidence (possibly spawning a new retrieval).
2. **Weaken.** Soften the claim to what evidence actually supports ("substantially higher" → "higher on the cited benchmark").
3. **Drop.** Remove the claim if it can't be supported.

Round cap: 3 reject rounds per section; exceeded → flag as "verifier_stalemate" and surface to user.

## Different-family requirement

The verifier uses a different family from the synthesis writer where possible. Same rationale as [Orion-Code's evaluator](../../orion-code/blocks/07-verifier-evaluator.md): shared blind-spot mitigation.

## Special handling for number-laden claims

Statistics, percentages, dates, named benchmarks — all extracted from the claim text and matched against the cited chunk. Mismatches are a hard reject (no LLM pass needed). This directly addresses the "fabricated number" failure mode prevalent in current Deep Research products.

## Output

A `VerificationReport`:

```json
{
  "total_claims": 64,
  "passed_pass1": 62,
  "passed_pass2": 58,
  "rejected": [
    {"claim_id": "...", "reason": "quoted string not found in source chunk",
     "pass": 1, "evidence_ids": ["..."]},
    {"claim_id": "...", "reason": "evidence discusses X but not Y",
     "pass": 2, "evidence_ids": ["..."]}
  ],
  "faithfulness_ratio": 0.906
}
```

The `faithfulness_ratio` is surfaced on the final report; reports below a floor (default 0.95) are not released without user acknowledgement.

## Failure modes

| Mode | Defense |
|---|---|
| Verifier is lenient | Rubric + structural checks first; hard rejects on number/quote mismatch |
| Source changed mid-flight | Freshness re-fetch; hash change detected |
| Verifier hallucinates "supported" | Structural checks before LLM; confidence threshold |
| Spurious rejects | Writer can escalate with additional evidence; stalemate flag |
| Cost blowup | Verification batched; cheap structural checks gate the LLM calls |

## Metrics

- `verifier.claim_count`, `verifier.pass1_reject_count`, `verifier.pass2_reject_count`
- `verifier.faithfulness_ratio` per report
- `verifier.round_count` per report
- `verifier.stalemate_count`
- `verifier.cost_usd` per report
