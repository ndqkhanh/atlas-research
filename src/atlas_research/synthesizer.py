"""Synthesis writer: Evidence[] + Brief → Report with claim-evidence binding."""
from __future__ import annotations

from .models import Brief, Claim, Evidence, Report, Section, SourceRef


class SynthesisWriter:
    """Produce a structured Report where every claim is bound to evidence IDs.

    MVP logic: one section per source-kind, one claim per evidence item.
    Real implementations call the LLM; the MVP is deterministic so the pipeline
    is testable without a model.
    """

    def write(self, brief: Brief, evidence: list[Evidence]) -> Report:
        if not evidence:
            return Report(
                brief=brief,
                sections=[Section(title="Findings", claims=[])],
                references=[],
            )

        sections_by_kind: dict[str, list[Claim]] = {}
        refs_by_id: dict[str, SourceRef] = {}

        for e in evidence:
            kind = e.source.kind.capitalize()
            sections_by_kind.setdefault(kind, [])
            sections_by_kind[kind].append(
                Claim(
                    text=_summarize(e.content),
                    evidence_ids=[e.id],
                )
            )
            refs_by_id[e.source.identifier] = e.source

        sections = [
            Section(title=f"{kind} findings", claims=claims)
            for kind, claims in sorted(sections_by_kind.items())
        ]

        return Report(
            brief=brief,
            sections=sections,
            references=list(refs_by_id.values()),
        )


def _summarize(content: str, max_sentences: int = 2) -> str:
    """Trivial summary: keep the first N sentence-ish spans."""
    parts = content.split(".")
    return ".".join(parts[:max_sentences]).strip() + "."
