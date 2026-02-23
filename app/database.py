import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _resolve_database_url() -> str:
    """
    Resolve DB URL with Supabase-friendly precedence.

    Priority:
    1) DATABASE_URL
    2) SUPABASE_DB_URL
    3) Local default postgres URL
    """
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or "postgresql+psycopg://postgres:postgres@localhost:5432/activity_tracker"
    )


DATABASE_URL = _resolve_database_url()

# Supabase requires TLS for remote connections.
# You can disable this by setting DB_SSLMODE=disable for local/dev DB.
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
connect_args = {"sslmode": DB_SSLMODE} if DATABASE_URL.startswith("postgresql+psycopg://") else {}

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
