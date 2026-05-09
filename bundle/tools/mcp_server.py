"""Atlas-Research MCP server stub.

Tools published:

- ``atlas.plan(question)`` — decompose into sub-queries.
- ``atlas.search(query, top_k)`` — web search for candidates.
- ``atlas.verify(claim, citation)`` — citation verification.
- ``atlas.synthesize(claims, sources)`` — final report.
- ``atlas.health()`` — adapter health.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    line = sys.stdin.readline()
    if not line.strip():
        print(json.dumps({"error": "no input"}))
        return 0
    req = json.loads(line)
    tool = req.get("tool", "atlas.health")
    args = req.get("args") or {}
    if tool == "atlas.plan":
        print(json.dumps({"tool": tool, "result": {
            "sub_queries": [
                {"query": "stub-1", "evidence_type": "paper", "priority": 1},
                {"query": "stub-2", "evidence_type": "blog", "priority": 2},
            ]
        }}))
    elif tool == "atlas.search":
        print(json.dumps({"tool": tool, "result": {"candidates": []}}))
    elif tool == "atlas.verify":
        print(json.dumps({"tool": tool, "result": {"status": "direct", "confidence": 0.9}}))
    elif tool == "atlas.synthesize":
        print(json.dumps({"tool": tool, "result": {"report": "<stub>", "claims": []}}))
    elif tool == "atlas.health":
        print(json.dumps({"tool": tool, "result": {"ok": True}}))
    else:
        print(json.dumps({"tool": tool, "error": f"unknown tool {tool}"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
