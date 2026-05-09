---
name: atlas-three-spoke
description: Lyra Agent Teams pattern — 3 parallel investigators.
team_kind: lead-pattern
default_model: smart
---
# Atlas Three-Spoke Investigation

The recommended pattern for non-trivial research questions: a
3-teammate Lyra Agent Teams ([`docs/250`](../../docs/250-anthropic-agent-teams.md))
fan-out:

```python
lead.spawn(TeammateSpec(name="scout", model="fast", subagent="atlas-scout"))
lead.spawn(TeammateSpec(name="verifier", model="smart", subagent="atlas-verifier"))
lead.spawn(TeammateSpec(name="synthesizer", model="smart", subagent="atlas-synth"))

scout_id = lead.add_task("draft 5 sub-queries", assign="scout")
verify_id = lead.add_task("verify candidates", assign="verifier", depends_on=[scout_id])
synth_id = lead.add_task("synthesize report", assign="synthesizer", depends_on=[verify_id])

lead.run_until_idle(timeout_s=900)
```

**Why three?** Per [`docs/224`](../../docs/224-multi-agent-parallel-scaling.md),
naturally-parallel investigation maps to roughly 3 spokes for
"recall × precision × synthesis". More spokes hit the diversity-
collapse failure ([`docs/98`](../../docs/98-diversity-collapse-mas.md)).

**Token cost:** ~7× single-session per Anthropic's documented Agent
Teams cost model. Use only when wall-clock saved exceeds dollars
spent — research questions where you'd otherwise wait minutes.
