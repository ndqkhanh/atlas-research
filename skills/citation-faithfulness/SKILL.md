---
name: 'citation-faithfulness'
description: 'Every emitted claim must cite an evidence chunk that lexically supports it.'
version: '0.1.0'
triggers: ['claim', 'citation']
tags: ['discipline', 'faithfulness']
---

# Goal
Emit no claim without an evidence citation that lexically supports it.

# Constraints & Style
- A claim is a sentence asserting a fact about the world.
- Every claim must cite an `evidence_id` from the retrieved set.
- Lexical overlap (≥ 0.5 Jaccard on content words) is required.
- If overlap fails, reject the claim and re-draft.

# Workflow
1. Identify each claim sentence in the draft.
2. For each claim, locate the cited evidence chunk.
3. Compute lexical overlap; reject below threshold.
4. Re-draft rejected claims with evidence in hand.
