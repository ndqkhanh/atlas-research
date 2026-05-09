"""Atlas-Research data model — briefs, evidence, claims, reports."""
from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Brief(BaseModel):
    """User-scoped research question."""

    question: str
    audience: str = "technical"
    style: str = "standard"  # terse | standard | exhaustive
    max_cost_usd: float = 3.0
    target_length_words: int = 2500
    time_window_days: Optional[int] = None


class SourceRef(BaseModel):
    """Handle pointing at an external source."""

    kind: str  # "web" | "arxiv" | "kb" | "db" | "mock"
    identifier: str  # URL / arxiv_id / kb_path / etc.
    title: str = ""
    published_at: Optional[str] = None


class Evidence(BaseModel):
    """A chunk of retrieved content bound to a source."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    source: SourceRef
    content: str
    relevance: float = 1.0


class Claim(BaseModel):
    """A statement in the draft with required evidence IDs."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    text: str
    evidence_ids: list[str]
    verified: bool = False
    verification_note: str = ""


class Section(BaseModel):
    title: str
    claims: list[Claim]


class Report(BaseModel):
    """Final output of the Atlas pipeline."""

    brief: Brief
    sections: list[Section]
    references: list[SourceRef]
    faithfulness_ratio: float = 1.0
    cost_usd: float = 0.0

    def to_markdown(self) -> str:
        """Render the report as markdown with numbered citations."""
        refs_by_id: dict[str, int] = {}
        for idx, ref in enumerate(self.references, start=1):
            refs_by_id[ref.identifier] = idx

        evidence_ref_map: dict[str, int] = {}
        for section in self.sections:
            for claim in section.claims:
                for eid in claim.evidence_ids:
                    # Heuristic: map each unique evidence id to its source's ref number
                    pass
        # Simpler: just number every cited evidence_id as-ordered
        citation_num: dict[str, int] = {}
        counter = 1
        lines = [f"# {self.brief.question}", ""]
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            for claim in section.claims:
                nums: list[int] = []
                for eid in claim.evidence_ids:
                    if eid not in citation_num:
                        citation_num[eid] = counter
                        counter += 1
                    nums.append(citation_num[eid])
                cite_str = " " + ",".join(f"[{n}]" for n in nums) if nums else ""
                suffix = "" if claim.verified else " *(unverified)*"
                lines.append(f"- {claim.text}{cite_str}{suffix}")
            lines.append("")
        lines.append("## References")
        lines.append("")
        for ref in self.references:
            lines.append(f"- [{ref.title or ref.identifier}]({ref.identifier})")
        lines.append("")
        lines.append(f"*faithfulness: {self.faithfulness_ratio:.0%}; cost: ${self.cost_usd:.2f}*")
        return "\n".join(lines)
