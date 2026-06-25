import json

from sqlmodel import Session, SQLModel, select

from src.database import NettingAudit, test_engine


def test_database_writes_and_reads_audit_record() -> None:
    """
    Test that the ORM can successfully create the table, insert a NettingAudit
    record, and retrieve it without data loss or schema violations.
    """
    # 1. Arrange: Build the schema in RAM
    SQLModel.metadata.create_all(test_engine)

    mock_ledger = {"GBP": {"Alice": "0.00", "Bob": "0.00"}}

    audit_record = NettingAudit(
        idempotency_key="db-test-key-001",
        base_currency="GBP",
        netted_balances_json=json.dumps(mock_ledger),
    )

    # 2. Act: Write to the database
    with Session(test_engine) as session:
        session.add(audit_record)
        session.commit()

    # 3. Assert: Read from the database
    with Session(test_engine) as session:
        statement = select(NettingAudit).where(
            NettingAudit.idempotency_key == "db-test-key-001"
        )
        retrieved_record = session.exec(statement).first()

        assert retrieved_record is not None
        assert retrieved_record.base_currency == "GBP"

        # Verify the JSON payload remained intact
        parsed_ledger = json.loads(retrieved_record.netted_balances_json)
        assert parsed_ledger["GBP"]["Alice"] == "0.00"
