"""Atlas-Research: long-horizon research agent.

Pipeline: intake → plan (ReWOO-style DAG) → retrieval → synthesis → citation verification.

Public API:
    - AtlasPipeline: orchestrates a full report
    - Report, Claim, Evidence, SourceRef: data model
    - CitationVerifier, QueryPlanner, Retriever, SynthesisWriter: pipeline stages
"""
from __future__ import annotations

from .models import Brief, Claim, Evidence, Report, SourceRef
from .pipeline import AtlasPipeline
from .planner import QueryPlanner
from .retriever import MockRetriever, Retriever
from .synthesizer import SynthesisWriter
from .verifier import CitationVerifier, VerificationReport

__all__ = [
    "AtlasPipeline",
    "Brief",
    "CitationVerifier",
    "Claim",
    "Evidence",
    "MockRetriever",
    "QueryPlanner",
    "Report",
    "Retriever",
    "SourceRef",
    "SynthesisWriter",
    "VerificationReport",
]
