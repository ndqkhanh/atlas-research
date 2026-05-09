"""Atlas-Research skills-adapter smoke test."""
from __future__ import annotations

from atlas_research.skills_adapter import (
    AtlasDocumentExtractor,
    AtlasPrefExtractor,
    AtlasSkillBank,
)

PAPER = """
Title: Sample Paper

Procedure:
1. Compute the input distribution.
2. Apply the proposed transform.
3. Measure output entropy.
4. Verify against baseline.
"""


def test_paper_yields_procedure_skill() -> None:
    ext = AtlasDocumentExtractor.default()
    out = ext.from_paper(doi="10.1/x", title="Sample Paper", body=PAPER, program_id="prog-1")
    assert len(out) == 1
    assert "10.1/x" == out[0].source_id


def test_user_feedback_yields_pref_skill() -> None:
    ext = AtlasPrefExtractor.default()
    turns = [{"role": "user", "content": "Always use IEEE citation style"}]
    out = ext.from_feedback(turns, program_id="prog-1")
    assert out


def test_program_namespace_isolation(tmp_path) -> None:
    a = AtlasSkillBank.for_program(tmp_path, program_id="p1")
    b = AtlasSkillBank.for_program(tmp_path, program_id="p2")
    assert a.bank.active_dir != b.bank.active_dir
