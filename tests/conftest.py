import asyncio
import os

from fastapi.testclient import TestClient
import pytest
from tortoise.contrib.test import finalizer, initializer

from src.api import app
from src.db import create_user


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    """
    https://tortoise-orm.readthedocs.io/en/latest/contrib/unittest.html
    """
    db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
    initializer(["src.db"], db_url=db_url, app_label="models")
    request.addfinalizer(finalizer)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
@pytest.mark.asyncio
async def user():
    user = await create_user("bob", "changeme")
    yield user
    await user.delete()


@pytest.fixture
def payload():
    return {"code": """print("hello world")"""}
