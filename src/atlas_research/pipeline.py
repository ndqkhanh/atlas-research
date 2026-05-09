"""AtlasPipeline: glue for planner → retriever → synthesizer → verifier."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from harness_core.observability import Tracer

from .models import Brief, Report
from .planner import QueryPlanner
from .retriever import MockRetriever, Retriever
from .synthesizer import SynthesisWriter
from .verifier import CitationVerifier, VerificationReport


@dataclass
class PipelineResult:
    report: Report
    verification: VerificationReport


class AtlasPipeline:
    """Full report pipeline — orchestrates stages with shared tracer."""

    def __init__(
        self,
        *,
        planner: Optional[QueryPlanner] = None,
        retriever: Optional[Retriever] = None,
        synthesizer: Optional[SynthesisWriter] = None,
        verifier: Optional[CitationVerifier] = None,
        tracer: Optional[Tracer] = None,
    ) -> None:
        self.planner = planner or QueryPlanner()
        self.retriever = retriever or MockRetriever()
        self.synthesizer = synthesizer or SynthesisWriter()
        self.verifier = verifier or CitationVerifier()
        self.tracer = tracer or Tracer()

    def run(self, brief: Brief) -> PipelineResult:
        with self.tracer.span("atlas.pipeline", question_preview=brief.question[:80]):
            with self.tracer.span("atlas.plan"):
                plan = self.planner.plan(brief.question)
            with self.tracer.span("atlas.retrieve", tasks=len(plan.tasks)):
                evidence = self.retriever.execute(plan)
            with self.tracer.span("atlas.synthesize", evidence=len(evidence)):
                report = self.synthesizer.write(brief, evidence)
            with self.tracer.span("atlas.verify"):
                verification = self.verifier.verify(report, evidence)
            report.cost_usd = round(plan.estimated_cost_usd, 2)

        return PipelineResult(report=report, verification=verification)
