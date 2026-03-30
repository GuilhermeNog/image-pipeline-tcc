import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import create_app

# Import all models so they register with Base.metadata
import app.models  # noqa: F401

# --- SQLite compat: render PostgreSQL UUID as CHAR(32) on SQLite ---
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # noqa: N811

@event.listens_for(Base.metadata, "column_reflect")
def _reflect_col(inspector, table, column_info):
    pass  # not needed for create_all, but kept as placeholder

# Monkey-patch: make PG UUID compile to CHAR(32) on SQLite
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID

@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(32)"

# --- end SQLite compat ---

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword123",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
