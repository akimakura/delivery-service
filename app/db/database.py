from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
_is_pytest = bool(os.getenv("PYTEST_CURRENT_TEST")) or os.getenv("TESTING") == "true"
if _is_pytest:
    # Use relaxed test settings with safe defaults
    from app.core.config_test import settings
else:
    from app.core.config import settings
from sqlalchemy.orm import declarative_base


# Use in-memory SQLite during tests to avoid external DB dependency
_database_url = "sqlite+aiosqlite:///./test.db" if _is_pytest else settings.DATABASE_URL

engine = create_async_engine(_database_url, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

_tables_created = False

async def get_session() -> AsyncSession:
    global _tables_created
    if _is_pytest and not _tables_created:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True
    async with AsyncSessionLocal() as s:
        yield s