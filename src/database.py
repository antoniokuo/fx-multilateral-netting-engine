import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Session, SQLModel, create_engine


class NettingAudit(SQLModel, table=True):
    """
    Immutable Audit Trail table.
    Records the final state of every successful multilateral netting execution.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    idempotency_key: str = Field(index=True, unique=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    base_currency: str
    netted_balances_json: str  # Storing the final graph as a serialized JSON string


# In-memory SQLite database strictly for the test suite
TEST_SQLITE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLITE_URL, echo=False, connect_args={"check_same_thread": False}
)

# Persistent local SQLite database for local execution/production
SQLITE_URL = "sqlite:///audit_trail.db"
engine = create_engine(
    SQLITE_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """Generates the SQLite file and builds the tables based on the schema."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:  # type: ignore
    """Dependency injector for FastAPI database sessions."""
    with Session(engine) as session:
        yield session
