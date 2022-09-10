import os

import databases
import pytest_asyncio

from authorization.api.infrastructure.datastore.postgres import ENTITY_TABLE, CHILD_ENTITY_TABLE
from authorization.api.infrastructure.entity_aggregate.entity_repo import PGEntityRepo
from authorization.api.tests import stub_entities


@pytest_asyncio.fixture
async def pg_client() -> databases.Database:
    pg_host = os.getenv("TEST_POSTGRES_HOST", default="localhost")
    pg_port = os.getenv("TEST_POSTGRES_PORT", default=5432)
    pg_user = os.getenv("TEST_POSTGRES_USER", default="postgres")
    pg_password = os.getenv("TEST_POSTGRES_PASSWORD", default="")
    pg_database = os.getenv("TEST_POSTGRES_DB", "entity_service_test")
    pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    pg_client = databases.Database(pg_url)
    await pg_client.connect()
    yield pg_client
    await pg_client.disconnect()


@pytest_asyncio.fixture
async def pg_db(pg_client) -> databases.Database:
    tables = [ENTITY_TABLE, CHILD_ENTITY_TABLE]

    for table in tables:
        async with pg_client.connection() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))

    yield

    for table in tables:
        async with pg_client.connection() as conn:
            await conn.execute("TRUNCATE TABLE {0} CASCADE".format(table.name))


@pytest_asyncio.fixture
async def pg_entity_repo(pg_client, pg_db) -> PGEntityRepo:
    repo = PGEntityRepo(pg_client)
    for stub_entity in stub_entities:
        await repo.create(stub_entity)
    return repo
