---
name: synthesis-rubric
description: Per-paragraph rubric the synthesizer follows.
---
# Synthesis Rubric

Every paragraph of the final report:

- Has a **topic sentence** that names the claim.
- Has at least **one inline citation** per claim. Multi-claim
  paragraphs have one per claim.
- Cites at least **two independent sources** for load-bearing claims
  (`LBL-ATLAS-DUAL-SOURCE`); single-source claims show
  `confidence ≤ 0.5` flag.
- Avoids **invention**: no claim the evidence doesn't support.
- Reports **uncertainty**: hedge language tied to confidence
  scores, not arbitrary "may", "might".

The synthesizer's output is JSON-serializable so reviewers can
walk paragraphs ↔ citations ↔ supporting spans without re-parsing.
