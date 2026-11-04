"""Demo fixtures with deliberately small, visible setup costs."""

import time

import pytest


@pytest.fixture(scope="session")
def settings():
    time.sleep(0.03)
    return {"currency": "USD", "retries": 3}


@pytest.fixture(scope="module")
def database(settings):
    time.sleep(0.02)
    return {"connected": True, "settings": settings}


@pytest.fixture(params=["en", "fr"])
def locale(request):
    time.sleep(0.005)
    return request.param


@pytest.fixture
def client(database):
    time.sleep(0.01)
    return {"db": database}
