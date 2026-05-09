---
title: Atlas-Research — Skills
description: AutoSkill4Doc paper-to-skill extraction + AutoSkill user-pref skills, both layered on the existing CitationVerifier.
---

# Atlas-Research — Skills

Atlas absorbs ideas from papers; the natural skill stream is **AutoSkill4Doc**
(paper → procedural skill). User-feedback skills follow vanilla AutoSkill.

## Corner of the design space

| Axis | Value |
|---|---|
| Feedback signal | Citation verifier (paper side); LLM judge (user-pref side) |
| Skill artifact | Single SKILL.md per paper procedure |
| Parameter access | Frozen weights |
| Reference paper | [AutoSkill](../../../docs/167-autoskill-experience-driven-lifelong-learning.md), [Ctx2Skill](../../../docs/154-ctx2skill-self-evolving-context-skills.md) |

## Adapter

`atlas_research.skills_adapter` provides:

- `AtlasDocumentExtractor` — wraps `harness_skills.extract.DocumentExtractor`,
  triggered by Retriever after a paper passes CitationVerifier.
- `AtlasPrefExtractor` — vanilla DialogueExtractor on user-feedback turns.
- Per-program SkillBank under `atlas/programs/<program-id>/skills/`.

## Bright-lines

- `BL-ATLAS-SKILL-PROMOTE` — paper-derived skills require human verification
  of source paper tier (peer-reviewed vs. preprint).

## Seed skills

- `citation-faithfulness` — every claim must cite an evidence chunk.
- `paper-tldr-procedure` — extract canonical TLDR from a paper.
