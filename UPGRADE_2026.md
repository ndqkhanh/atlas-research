# Atlas-Research — May-2026 Upgrade Stub

> Companion to [`../CROSS_PROJECT_UPGRADE_PLAN_2026.md`](../CROSS_PROJECT_UPGRADE_PLAN_2026.md). Per the
> cross-project matrix, Atlas-Research is **W2** — bundle the research
> agent and adopt Lyra Agent Teams ([`docs/250`](../../docs/250-anthropic-agent-teams.md))
> for naturally-parallel investigations (3 teammates: scout, verifier,
> synthesizer).

## Headline gap (vs 2026 SOTA)

- **Mock retriever** — no real web search; the pipeline shape is
  correct but production needs a real MCP search server.
- **No `bundle/`** — query planner + citation verifier not packaged.
- **No parallel investigation** — current pipeline is sequential
  ReWOO; the 2026 SOTA pattern (per [`docs/226`](../../docs/226-gpt-researcher-deep-research-platform.md)
  GPT-Researcher) is 3+ parallel investigators with cross-source
  citation reconciliation.

## Smallest upgrade

```text
atlas-research/bundle/
├── bundle.yaml
├── persona.md                 # "you are a long-horizon research agent..."
├── skills/
│   ├── 01-query-planner.md
│   ├── 02-citation-verifier.md
│   ├── 03-synthesis-rubric.md
│   └── 04-faithfulness-gate.md
├── tools/
│   └── mcp_server.py          # exposes search + extract + cite via MCP
├── memory/
│   └── seed.md                # default citation style + faithfulness rules
├── evals/
│   ├── golden.jsonl           # 30+ research-question → cited-answer evals
│   └── rubric.md              # GAIA + BrowseComp rubric
└── verifier/
    └── checker.py             # citation-coverage check
```

## Lyra Agent Teams pattern (3-spoke parallel investigation)

Once the bundle is live, the canonical Atlas usage from Lyra is:

```python
lead = LeadSession.create(team_name="research-q42", ...)
lead.spawn(TeammateSpec(name="scout", model="fast", subagent="atlas-scout"))
lead.spawn(TeammateSpec(name="verifier", model="smart", subagent="atlas-verifier"))
lead.spawn(TeammateSpec(name="synthesizer", model="smart", subagent="atlas-synth"))

lead.add_task("draft 5 sub-questions for: ...", assign="scout")
lead.add_task("for each scout claim, find 2 independent sources",
              assign="verifier", depends_on=[scout_task_id])
lead.add_task("synthesize verified claims into 600-word brief",
              assign="synthesizer", depends_on=[verifier_task_id])
lead.run_until_idle(timeout_s=900)
```

This realizes the [`docs/250`](../../docs/250-anthropic-agent-teams.md)
"multi-hypothesis investigation" recommended pattern (K=5 with 3-4
tasks each) — the project's 3-role pipeline maps directly onto Lyra's
shared task list + dependency graph.

## Test plan

- 8+ tests covering bundle validation, MCP search server stub, citation
  verifier rubric, faithfulness gate, and a 3-spoke Agent Teams smoke
  test against a canned 5-question set.

## Sequencing

W2 — depends on Lyra v3.11 L311-1 (Agent Teams runtime) + L311-4 / L311-5
(bundle).

## Related Lyra phases

- L311-1 Agent Teams runtime — enables the 3-spoke parallel pattern.
- L311-4 SourceBundle — defines the bundle contract.
- L311-6 Verifier coverage — the bundle's citation-verifier feeds the
  research-domain coverage score.
