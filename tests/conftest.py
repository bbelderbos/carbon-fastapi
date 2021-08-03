import asyncio

import pytest


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    return asyncio.get_event_loop()
