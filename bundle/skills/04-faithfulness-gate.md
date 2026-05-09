---
name: faithfulness-gate
description: Final pass — every claim survives an independent re-verify.
---
# Faithfulness Gate

After synthesis, a separate pass re-verifies every claim against its
citation. The gate exists to catch:

- Drift between draft and final (synthesizer paraphrased away from
  the source).
- Citation drift (the link points somewhere different now).
- Hallucinated qualifiers ("widely accepted", "decades of research")
  that don't appear in the cited source.

The gate uses a *different judge family* from the synthesizer
(decorrelation), per the Vertex-Eval pairwise-decorrelation pattern.

A claim that fails the gate is **rewritten or removed**. Reports
ship only after the gate is green; a flagged claim that the user
overrides ships with an explicit `LBL-ATLAS-OVERRIDE` annotation.
