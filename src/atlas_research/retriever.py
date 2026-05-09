"""Retriever abstraction + MockRetriever that returns canned results.

Real deployments plug in an MCP-backed search server via a custom Retriever.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .models import Evidence, SourceRef
from .planner import QueryPlan, QueryTask


class Retriever(ABC):
    @abstractmethod
    def execute(self, plan: QueryPlan) -> list[Evidence]:  # pragma: no cover - abstract
        raise NotImplementedError


class MockRetriever(Retriever):
    """Returns a fixed, plausible evidence set for any plan.

    Override ``canned_evidence`` to script specific test scenarios.
    """

    def __init__(self, canned_evidence: Optional[list[Evidence]] = None) -> None:
        self._canned = canned_evidence

    def execute(self, plan: QueryPlan) -> list[Evidence]:
        if self._canned is not None:
            return list(self._canned)

        # Generate a small, deterministic evidence set based on plan tasks.
        evidence: list[Evidence] = []
        for task in plan.tasks:
            if task.kind in ("web_search", "fetch_url"):
                query = task.args.get("query", task.id)
                evidence.append(
                    Evidence(
                        source=SourceRef(
                            kind="web",
                            identifier=f"https://example.com/search/{task.id}",
                            title=f"Web result for {query}",
                        ),
                        content=(
                            f"Mock web content discussing {query}. "
                            "This is canned evidence produced by MockRetriever; "
                            "swap in a real MCP search server for production."
                        ),
                        relevance=0.9,
                    )
                )
            elif task.kind == "arxiv_search":
                query = task.args.get("query", task.id)
                evidence.append(
                    Evidence(
                        source=SourceRef(
                            kind="arxiv",
                            identifier=f"arxiv:{task.id}.00000",
                            title=f"Arxiv paper on {query}",
                            published_at="2026-04",
                        ),
                        content=(
                            f"Abstract: we present work on {query}. "
                            "Our method improves prior baselines by an unspecified margin."
                        ),
                        relevance=0.85,
                    )
                )
        return evidence


def _find_task(plan: QueryPlan, task_id: str) -> Optional[QueryTask]:
    return next((t for t in plan.tasks if t.id == task_id), None)
