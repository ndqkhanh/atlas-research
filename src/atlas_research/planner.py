"""Query planner: Brief → list of retrieval tasks (ReWOO-style)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QueryTask:
    id: str
    kind: str  # "web_search" | "arxiv_search" | "fetch_url"
    args: dict
    depends_on: list[str] = field(default_factory=list)


@dataclass
class QueryPlan:
    tasks: list[QueryTask]
    estimated_cost_usd: float = 0.0


class QueryPlanner:
    """Deterministic planner that decomposes a brief into retrieval tasks.

    In production this would call a strong LLM; the MVP uses a simple rule set
    that produces a ~4-task plan covering web + arxiv + fetch of top hit.
    """

    def plan(self, question: str, *, max_tasks: int = 5) -> QueryPlan:
        if not question.strip():
            raise ValueError("empty question")

        tasks: list[QueryTask] = [
            QueryTask(
                id="E1",
                kind="web_search",
                args={"query": question, "k": 5},
            ),
            QueryTask(
                id="E2",
                kind="arxiv_search",
                args={"query": question, "max_results": 5},
            ),
            QueryTask(
                id="E3",
                kind="fetch_url",
                args={"from": "E1", "index": 0},
                depends_on=["E1"],
            ),
        ]
        return QueryPlan(tasks=tasks[:max_tasks], estimated_cost_usd=0.05 * len(tasks))
