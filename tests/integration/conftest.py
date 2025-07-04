from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from alembic.config import Config
from alembic import command
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.main.web import main

from tests.integration.helpers.db_setup import ensure_test_db_exists, truncate_all_tables


@pytest.fixture
async def test_get_token(client: AsyncClient) -> str:
    token = await client.get(f'/oauth')
    return token.json()

@pytest.fixture
async def created_user(client: AsyncClient):
    user = await client.post(
        f'/users',
        data={
            'username': 'test',
            'email': 'test@example.com',
            'password': '123123',
        }
    )
    return user.json()

@pytest.fixture
def sync_db_url() -> str:
    return 'postgresql://admin:admin123@localhost:5432/test_pure_soul'
@pytest.fixture
def db_url() -> str:
    return 'postgresql+asyncpg://admin:admin123@localhost:5432/test_pure_soul'


@asynccontextmanager
async def run_migrations(db_url: str, sync_db_url: str):
    ensure_test_db_exists(sync_db_url)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")
    yield
    truncate_all_tables(sync_db_url)


@pytest.fixture
def session_factory(db_url) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        url=db_url,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)
    return session_factory

@pytest_asyncio.fixture
async def db_session(session_factory: async_sessionmaker[AsyncSession], sync_db_url, db_url) -> AsyncSession:
    async with run_migrations(db_url=db_url, sync_db_url=sync_db_url) as _:
        async with session_factory() as session:
            yield lambda: session
            await session.rollback()

@pytest.fixture
def app(db_session):
    app = main(
        token_secret = 'secret',
        s3_uri = 'http://127.0.0.1:9000',
        s3_access_key_id = 'mRa7SfDQPxvAr7OX1loRaAyfHf2JX4PC9iqhBUU8',
        s3_secret_key = 'cPXy2dJM4im3iRjApIWw',
        db_url="fake"
    )
    app.dependency_overrides.update({
        TransactionManager: db_session,
    })
    return app

@pytest_asyncio.fixture
async def client(app: FastAPI):
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://test") as c:
        yield c
