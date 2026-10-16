import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["ANALYTICS_API_KEY"] = "test-assigned-key"
from main import app  # noqa: E402

client = TestClient(app)


def test_requires_key_when_missing():
    response = client.post("/analytics", json={"events": []})
    assert response.status_code == 401


def test_requires_correct_key():
    response = client.post(
        "/analytics",
        headers={"X-API-Key": "wrong-key"},
        json={"events": []},
    )
    assert response.status_code == 401


def test_aggregates_fresh_batch_and_ignores_nonpositive_revenue():
    events = [
        {"user": "alice", "amount": 12.5, "ts": 1700000000},
        {"user": "bob", "amount": 21.0, "ts": 1700000001},
        {"user": "alice", "amount": -5.0, "ts": 1700000002},
        {"user": "cara", "amount": 15.0, "ts": 1700000003},
        {"user": "bob", "amount": 3.0, "ts": 1700000004},
        {"user": "cara", "amount": 0.0, "ts": 1700000005},
    ]
    response = client.post(
        "/analytics",
        headers={"X-API-Key": "test-assigned-key"},
        json={"events": events},
    )
    assert response.status_code == 200
    assert response.json() == {
        "email": "23f2000363@ds.study.iitm.ac.in",
        "total_events": 6,
        "unique_users": 3,
        "revenue": 51.5,
        "top_user": "bob",
    }


def test_cors_allows_cross_origin_post():
    response = client.options(
        "/analytics",
        headers={
            "Origin": "https://example.exam",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-key",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"


def test_empty_events_is_computed():
    response = client.post(
        "/analytics",
        headers={"X-API-Key": "test-assigned-key"},
        json={"events": []},
    )
    assert response.status_code == 200
    assert response.json()["total_events"] == 0
    assert response.json()["unique_users"] == 0
    assert response.json()["revenue"] == 0.0
    assert response.json()["top_user"] is None
