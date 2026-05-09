---
name: citation-verifier
description: Verify every cited source actually supports the claim.
---
# Citation Verifier

For every (claim, citation) pair:

1. Re-fetch the source (cache hit when possible).
2. Locate the *supporting span* in the source.
3. Score the support: `direct` / `partial` / `tangential` / `unsupported`.

**Bright line `LBL-ATLAS-FAITHFUL`:** `unsupported` and `tangential`
fail; `partial` produces a confidence flag (≤0.5).

The verifier emits `atlas.citation.<status>` events on every check.
