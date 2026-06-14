import uuid

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_api_executes_idempotent_netting() -> None:
    """
    Test that the API accepts a JSON payload, executes the netting algorithm,
    and rigorously enforces idempotency (returning cached results for duplicate keys).
    """
    # 1. Arrange: The JSON Payload
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

    idempotency_key = "idem-test-key-001"
    headers = {"Idempotency-Key": idempotency_key}

    # 2. Act: First Request
    response_1 = client.post("/api/v1/netting/clear", json=payload, headers=headers)

    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1["balances"]["GBP"]["Alice"] == "-30.00"
    assert data_1["balances"]["GBP"]["Bob"] == "30.00"
    assert data_1["cached"] is False

    # 3. Act: Second (Duplicate) Request
    response_2 = client.post("/api/v1/netting/clear", json=payload, headers=headers)

    # 4. Assert: Idempotency Protection
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["balances"] == data_1["balances"]
    assert data_2["cached"] is True  # Proves the math was bypassed
