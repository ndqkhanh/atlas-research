"""End-to-end tests of the Atlas pipeline."""
from __future__ import annotations

import pytest
from atlas_research import (
    AtlasPipeline,
    Brief,
    CitationVerifier,
    Claim,
    Evidence,
    MockRetriever,
    QueryPlanner,
    Report,
    SourceRef,
    SynthesisWriter,
)
from atlas_research.models import Section


def test_planner_produces_nonempty_plan():
    plan = QueryPlanner().plan("What is Orion-Code?")
    assert len(plan.tasks) >= 1
    assert plan.estimated_cost_usd > 0


def test_planner_rejects_empty_question():
    with pytest.raises(ValueError, match="empty question"):
        QueryPlanner().plan("   ")


def test_mock_retriever_returns_evidence_per_task():
    plan = QueryPlanner().plan("example")
    evidence = MockRetriever().execute(plan)
    assert len(evidence) >= 1
    # each should have an id, source, and content
    assert all(e.id and e.source and e.content for e in evidence)


def test_synthesizer_binds_claims_to_evidence():
    brief = Brief(question="Q?")
    evidence = [
        Evidence(
            source=SourceRef(kind="web", identifier="https://e.com/a", title="A"),
            content="Alpha discusses foo bar baz.",
        ),
        Evidence(
            source=SourceRef(kind="arxiv", identifier="arxiv:2000.00001", title="X"),
            content="X proposes quux for foo.",
        ),
    ]
    report = SynthesisWriter().write(brief, evidence)
    all_claims = [c for s in report.sections for c in s.claims]
    assert all_claims  # at least one claim
    assert all(c.evidence_ids for c in all_claims)  # all bound


def test_synthesizer_empty_evidence_produces_empty_findings():
    brief = Brief(question="Q?")
    report = SynthesisWriter().write(brief, [])
    assert len(report.sections) == 1
    assert report.sections[0].claims == []


def test_verifier_passes_supported_claim():
    evidence = [
        Evidence(
            id="e1",
            source=SourceRef(kind="web", identifier="u1"),
            content="rollout strategies discussed in detail.",
        )
    ]
    report = Report(
        brief=Brief(question="x"),
        sections=[
            Section(
                title="s",
                claims=[Claim(text="rollout strategies overview", evidence_ids=["e1"])],
            )
        ],
        references=[],
    )
    vr = CitationVerifier().verify(report, evidence)
    assert vr.verified_claims == 1
    assert vr.total_claims == 1
    assert vr.faithfulness_ratio == 1.0


def test_verifier_rejects_claim_with_missing_evidence():
    report = Report(
        brief=Brief(question="x"),
        sections=[
            Section(
                title="s",
                claims=[Claim(text="orphan claim", evidence_ids=["ghost-id"])],
            )
        ],
        references=[],
    )
    vr = CitationVerifier().verify(report, evidence=[])
    assert vr.verified_claims == 0
    assert "not found" in vr.rejected[0][1]


def test_verifier_rejects_claim_with_no_lexical_overlap():
    evidence = [
        Evidence(
            id="e1",
            source=SourceRef(kind="web", identifier="u1"),
            content="completely unrelated topic about weather.",
        )
    ]
    report = Report(
        brief=Brief(question="x"),
        sections=[
            Section(
                title="s",
                claims=[Claim(text="quantum entanglement", evidence_ids=["e1"])],
            )
        ],
        references=[],
    )
    vr = CitationVerifier().verify(report, evidence)
    assert vr.verified_claims == 0
    assert "lexical overlap" in vr.rejected[0][1]


def test_pipeline_full_run_produces_verified_markdown():
    pipeline = AtlasPipeline()
    result = pipeline.run(Brief(question="What is harness engineering?"))
    md = result.report.to_markdown()
    assert "# What is harness engineering?" in md
    assert "References" in md
    # With MockRetriever's deterministic evidence, most or all claims verify
    assert result.verification.total_claims >= 1
    assert result.report.faithfulness_ratio >= 0.5


def test_report_markdown_numbers_citations():
    evidence = [
        Evidence(
            id="e1",
            source=SourceRef(kind="web", identifier="u1", title="W"),
            content="alpha beta gamma",
        ),
        Evidence(
            id="e2",
            source=SourceRef(kind="arxiv", identifier="u2", title="A"),
            content="gamma delta epsilon",
        ),
    ]
    brief = Brief(question="Q?")
    report = SynthesisWriter().write(brief, evidence)
    CitationVerifier().verify(report, evidence)
    md = report.to_markdown()
    assert "[1]" in md
    assert "[2]" in md
