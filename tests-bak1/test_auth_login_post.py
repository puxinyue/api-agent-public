from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_login_success():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "zhangsan",
        "password": "hashed_password_1"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "access_token" in data
    assert "token_type" in data

def test_login_invalid_credentials():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_login_missing_required_fields():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "testuser"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_login_empty_fields():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "",
        "password": ""
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data