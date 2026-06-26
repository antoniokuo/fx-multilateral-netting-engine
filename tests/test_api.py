import uuid

from fastapi.testclient import TestClient

from src.api import app


def test_api_executes_idempotent_netting() -> None:
    """
    Test that the API accepts a JSON payload, executes the netting algorithm,
    and rigorously enforces idempotency (returning cached results for duplicate keys).
    """
    payload = {
        "transactions": [
            {
                "id": str(uuid.uuid4()),
                "timestamp": "2026-06-14T10:00:00Z",
                "debtor": "Alice",
                "creditor": "Bob",
                "currency": "GBP",
                "amount": "50.00",
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": "2026-06-14T10:05:00Z",
                "debtor": "Bob",
                "creditor": "Alice",
                "currency": "GBP",
                "amount": "20.00",
            },
        ],
        "base_currency": "GBP",
    }

    # Generate a dynamic key to prevent SQLite Integrity collisions on repeat test runs
    idempotency_key = f"idem-test-{uuid.uuid4()}"
    headers = {"Idempotency-Key": idempotency_key}

    # Using TestClient as a context manager forces the FastAPI
    # lifespan event to trigger, ensuring create_db_and_tables()
    # executes before routing the request.
    with TestClient(app) as client:
        # 1. Act: First Request
        response_1 = client.post("/api/v1/netting/clear", json=payload, headers=headers)

        assert response_1.status_code == 200
        data_1 = response_1.json()
        assert data_1["balances"]["GBP"]["Alice"] == "-30.00"
        assert data_1["balances"]["GBP"]["Bob"] == "30.00"
        assert data_1["cached"] is False

        # 2. Act: Second (Duplicate) Request
        response_2 = client.post("/api/v1/netting/clear", json=payload, headers=headers)

        # 3. Assert: Idempotency Protection
        assert response_2.status_code == 200
        data_2 = response_2.json()
        assert data_2["balances"] == data_1["balances"]
        assert data_2["cached"] is True
