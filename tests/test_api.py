from textwrap import dedent

import pytest


def test_cannot_access_without_login(client, payload):
    response = client.post(
        "/images",
        json=payload)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_wrong_login(client, user, payload):
    response = client.post(
        "/token", data={"username": "bob", "password": "handl3bar"})
    assert response.status_code == 401


@pytest.fixture
def token(client, user):
    response = client.post(
        "/token",
        data={"username": "bob", "password": "changeme"})
    assert response.status_code == 200
    resp_dict = response.json()
    assert resp_dict["token_type"] == "bearer"
    return f"Bearer {resp_dict['access_token']}"


def test_create_code_image(client, token, payload):
    response = client.post(
        "/images", json=payload,
        headers={"Authorization": token})
    assert response.status_code == 201
    assert response.headers["content-type"] == "image/png"
    assert response.headers["content-length"] == '14443'
    # TODO test image output / diff real image?


def test_create_mindset_tip_image(client, token, payload):
    quote = """
        "Don't worry about getting it right. Just get it started."
        - Marie Forleo
    """
    payload["code"] = dedent(quote).strip()
    payload["parameters"] = {
        "backgroundColor": "C4F2FD",
        "theme": "Material",
        "language": "Plain Text",
    }
    response = client.post(
        "/images", json=payload,
        headers={"Authorization": token})
    assert response.status_code == 201
    assert response.headers["content-type"] == "image/png"
    assert response.headers["content-length"] == '19674'
