# PROMPT: Write a pytest suite for a FastAPI POST /ingest endpoint. The payload is a list of tracking events. I need to test that it successfully ingests data, handles idempotency (if the same event_id is sent twice, it ignores the duplicate), and handles partial success if one event is missing required fields.
# CHANGES MADE: I updated the HTTPX client setup to override the FastAPI get_current_user dependency so it doesn't require a valid JWT token. I also switched to FastAPI's native TestClient used within a context manager (`with TestClient(app) as client:`) to ensure the ASGI lifespan startup events (MongoDB connection) trigger correctly before the tests run.

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.dependencies import get_current_user

# Mock authentication to bypass login during tests
def override_get_current_user():
    return {"username": "test_admin", "role": "admin"}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_ingest_idempotency():
    """Tests that sending the exact same event twice only records it once."""
    event_payload = [{
        "event_id": "test-uuid-1234",
        "store_id": "STORE_BLR_002",
        "camera_id": "CAM_ENTRY_01",
        "visitor_id": "VIS_TEST_01",
        "event_type": "ENTRY",
        "timestamp": "2026-04-10T12:00:00Z",
        "zone_id": None,
        "dwell_ms": 0,
        "is_staff": False,
        "confidence": 0.95,
        "metadata": {"queue_depth": None}
    }]

    # The 'with' block forces the database to connect before running the test
    with TestClient(app) as client:
        # First send (Should Process)
        response1 = client.post("/api/events/ingest", json=event_payload)
        assert response1.status_code == 201
        data1 = response1.json()
        assert data1["processed"] == 1
        
        # Second send of the EXACT same payload (Should register as Duplicate)
        response2 = client.post("/api/events/ingest", json=event_payload)
        assert response2.status_code == 201
        data2 = response2.json()
        assert data2["duplicates"] == 1
        assert data2["processed"] == 0

def test_ingest_partial_success():
    """Tests that a malformed event doesn't crash the whole batch."""
    mixed_payload = [
        {
            "event_id": "test-uuid-valid",
            "store_id": "STORE_BLR_002",
            "camera_id": "CAM_ENTRY_01",
            "visitor_id": "VIS_TEST_02",
            "event_type": "ENTRY",
            "timestamp": "2026-04-10T12:05:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.99
        },
        {
            # MISSING event_id AND visitor_id (Invalid schema)
            "store_id": "STORE_BLR_002",
            "event_type": "ENTRY",
            "timestamp": "2026-04-10T12:05:00Z"
        }
    ]

    with TestClient(app) as client:
        response = client.post("/api/events/ingest", json=mixed_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "partial_success"
        assert data["processed"] == 1
        assert data["failed"] == 1