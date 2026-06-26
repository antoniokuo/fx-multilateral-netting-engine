import json
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from src.database import NettingAudit, create_db_and_tables, get_session
from src.engine import calculate_net_balances
from src.models import Transaction as DomainTransaction

# Temporary local cache for Idempotency tracking (RAM-bounded)
IDEMPOTENCY_CACHE: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handles application startup and shutdown lifecycle tasks."""
    create_db_and_tables()
    yield
    IDEMPOTENCY_CACHE.clear()


app = FastAPI(title="FX Multilateral Netting Engine API", lifespan=lifespan)


# --- Pydantic Data Transfer Objects (DTOs) ---
class TransactionInput(BaseModel):
    id: str
    timestamp: datetime
    debtor: str
    creditor: str
    currency: str = Field(..., min_length=3, max_length=3)
    amount: str


class NettingRequest(BaseModel):
    base_currency: str
    transactions: List[TransactionInput]


# --- HTTP Endpoints ---
@app.post("/api/v1/netting/clear")
async def clear_ledger(
    payload: NettingRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Ingests a ledger, executes the netting algorithm, persists the result
    to an immutable audit trail, and returns the optimised graph.
    """
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")

    # 1. Idempotency Firewall
    if idempotency_key in IDEMPOTENCY_CACHE:
        return IDEMPOTENCY_CACHE[idempotency_key]

    # 2. Domain Translation
    internal_ledger = []
    for t in payload.transactions:
        try:
            tx = DomainTransaction(
                id=t.id,
                timestamp=t.timestamp,
                debtor=t.debtor,
                creditor=t.creditor,
                currency=t.currency.upper(),
                amount=Decimal(t.amount),
            )
            internal_ledger.append(tx)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        # 3. Computational Layer
        netted_balances = calculate_net_balances(internal_ledger)

        # 4. JSON Serialisation
        json_safe_balances = {
            currency: {
                entity: str(amount) for entity, amount in entity_balances.items()
            }
            for currency, entity_balances in netted_balances.items()
        }

        # 5. Persistence Layer (Audit Trail)
        audit_record = NettingAudit(
            idempotency_key=idempotency_key,
            base_currency=payload.base_currency,
            netted_balances_json=json.dumps(json_safe_balances),
        )
        db.add(audit_record)
        db.commit()

        # 6. Cache Layer
        response_payload: Dict[str, Any] = {
            "status": "success",
            "balances": json_safe_balances,
            "cached": False,
        }

        cached_payload = response_payload.copy()
        cached_payload["cached"] = True
        IDEMPOTENCY_CACHE[idempotency_key] = cached_payload

        return response_payload

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Execution failure: {str(e)}")
