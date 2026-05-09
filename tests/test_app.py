"""HTTP surface tests for Atlas-Research."""
from __future__ import annotations

from atlas_research.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["service"] == "atlas-research"


def test_create_report_returns_markdown():
    r = client.post(
        "/v1/reports",
        json={"question": "What is a harness?"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "What is a harness?" in body["markdown"]
    assert body["total_claims"] >= 1
    assert 0.0 <= body["faithfulness_ratio"] <= 1.0


def test_create_report_validates_bounds():
    r = client.post(
        "/v1/reports",
        json={"question": "x", "max_cost_usd": -1.0},
    )
    assert r.status_code == 422  # pydantic validation
