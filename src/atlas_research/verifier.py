"""Citation verifier: every claim must have a resolvable, supportive evidence id."""
from __future__ import annotations

from dataclasses import dataclass

from .models import Claim, Evidence, Report


@dataclass
class VerificationReport:
    total_claims: int
    verified_claims: int
    rejected: list[tuple[str, str]]  # [(claim_id, reason)]

    @property
    def faithfulness_ratio(self) -> float:
        if self.total_claims == 0:
            return 1.0
        return self.verified_claims / self.total_claims


class CitationVerifier:
    """Walk a report's claims and verify each against the evidence store."""

    def verify(self, report: Report, evidence: list[Evidence]) -> VerificationReport:
        by_id: dict[str, Evidence] = {e.id: e for e in evidence}

        total = 0
        verified = 0
        rejected: list[tuple[str, str]] = []

        for section in report.sections:
            for claim in section.claims:
                total += 1
                reason = self._verify_claim(claim, by_id)
                if reason is None:
                    claim.verified = True
                    verified += 1
                else:
                    claim.verified = False
                    claim.verification_note = reason
                    rejected.append((claim.id, reason))

        vr = VerificationReport(
            total_claims=total,
            verified_claims=verified,
            rejected=rejected,
        )
        report.faithfulness_ratio = vr.faithfulness_ratio
        return vr

    @staticmethod
    def _verify_claim(claim: Claim, evidence_by_id: dict[str, Evidence]) -> str | None:
        if not claim.evidence_ids:
            return "no evidence bound"
        for eid in claim.evidence_ids:
            if eid not in evidence_by_id:
                return f"evidence id {eid!r} not found"
        # MVP: also require the claim text to share at least one meaningful token
        # with any cited evidence.
        claim_tokens = _tokens(claim.text)
        for eid in claim.evidence_ids:
            ev = evidence_by_id[eid]
            if claim_tokens & _tokens(ev.content):
                return None
        return "claim has no lexical overlap with cited evidence"


_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for",
    "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "with", "by", "as", "at",
    "we", "our", "our", "it", "its",
}


def _tokens(text: str) -> set[str]:
    return {
        t.strip(".,;:!?\"'()[]").lower()
        for t in text.split()
        if len(t) > 3 and t.strip(".,;:!?\"'()[]").lower() not in _STOPWORDS
    }
