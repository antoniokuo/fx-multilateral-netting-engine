from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.engine import calculate_net_balances
from src.models import Transaction

app = FastAPI(title="Multilateral Netting Engine API")

# In-memory Idempotency Cache: Maps Idempotency-Key -> Response Dict
# In production, this would be a Redis instance.
idempotency_cache: Dict[str, Dict[str, Any]] = {}


# --- Pydantic Data Transfer Objects (DTOs) ---
class TransactionInput(BaseModel):
    id: str
    timestamp: datetime
    debtor: str
    creditor: str
    currency: str = Field(..., min_length=3, max_length=3)
    amount: str  # Passed as string to preserve precision before Decimal conversion


class NettingPayload(BaseModel):
    transactions: List[TransactionInput]
    base_currency: str


# --- HTTP Endpoints ---
@app.post("/api/v1/netting/clear")
async def clear_network(
    payload: NettingPayload,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    """
    Accepts a JSON ledger, translates it to internal domain models,
    and returns the optimized net balances. Enforces idempotency via headers.
    """
    if not idempotency_key:
        raise HTTPException(
            status_code=400, detail="Idempotency-Key header is strictly required."
        )

    # 1. Idempotency Firewall
    if idempotency_key in idempotency_cache:
        return idempotency_cache[idempotency_key]

    # 2. Domain Translation (Pydantic -> Internal Models)
    internal_ledger = []
    for t in payload.transactions:
        try:
            tx = Transaction(
                id=t.id,
                # FastAPI parses ISO8601 strings into
                # timezone-aware datetimes automatically
                timestamp=t.timestamp,
                debtor=t.debtor,
                creditor=t.creditor,
                currency=t.currency.upper(),
                amount=Decimal(t.amount),
            )
            internal_ledger.append(tx)
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Data Boundary Violation: {str(e)}"
            )

    # 3. Mathematical Execution
    net_balances = calculate_net_balances(internal_ledger)

    # 4. JSON Serialization (Decimals must be cast to strings for HTTP)
    json_safe_balances = {
        currency: {entity: str(amount) for entity, amount in entity_balances.items()}
        for currency, entity_balances in net_balances.items()
    }

    response_data = {
        "status": "success",
        "balances": json_safe_balances,
        "cached": False,
    }

    # 5. Lock the State
    # We alter the cached payload so future requests visibly identify as cached.
    cached_response = response_data.copy()
    cached_response["cached"] = True
    idempotency_cache[idempotency_key] = cached_response

    return response_data
