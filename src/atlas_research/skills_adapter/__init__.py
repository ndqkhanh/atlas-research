"""Atlas-Research skills adapter — paper-to-skill + user-pref."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_skills import SkillRecord
from harness_skills.extract import DialogueExtractor, DocumentExtractor, ExtractionContext
from harness_skills.store import SkillBank


@dataclass
class AtlasDocumentExtractor:
    extractor: DocumentExtractor

    @classmethod
    def default(cls) -> AtlasDocumentExtractor:
        return cls(extractor=DocumentExtractor(family="extractor-atlas"))

    def from_paper(self, *, doi: str, title: str, body: str, program_id: str) -> list[SkillRecord]:
        return self.extractor.extract(
            {"text": body, "title": title, "doi": doi},
            context=ExtractionContext(session_id=program_id, program_id=program_id),
        )


@dataclass
class AtlasPrefExtractor:
    extractor: DialogueExtractor

    @classmethod
    def default(cls) -> AtlasPrefExtractor:
        return cls(extractor=DialogueExtractor(family="extractor-atlas"))

    def from_feedback(self, turns: list[dict], program_id: str) -> list[SkillRecord]:
        return self.extractor.extract(turns, context=ExtractionContext(session_id=program_id, program_id=program_id))


@dataclass
class AtlasSkillBank:
    bank: SkillBank

    @classmethod
    def for_program(cls, root: Path | str, program_id: str) -> AtlasSkillBank:
        return cls(bank=SkillBank(root=root, namespace=f"programs/{program_id}"))


__all__ = ["AtlasDocumentExtractor", "AtlasPrefExtractor", "AtlasSkillBank"]
