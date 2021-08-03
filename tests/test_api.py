from fastapi.testclient import TestClient
import pytest
# from httpx import AsyncClient

from src.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_cannot_access_without_login(client):
    response = client.get(f"/users/me/items/")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_read_item(client):
    response = client.post(
        "/token", data={"username": "bob", "password": "handl3bar"})
    assert response.status_code == 200
    resp_dict = response.json()
    assert resp_dict["token_type"] == "bearer"
    access_token = f"Bearer {resp_dict['access_token']}"
    response = client.get(
        "/users/me/items/", headers={"Authorization": access_token})
    assert response.status_code == 200
    assert response.json() == [{'item_id': 'Foo', 'owner': 'bob'}]
