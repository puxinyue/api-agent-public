from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_register_success():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_register_username_exists(valid_token):
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "existinguser",
        "password": "testpassword",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 409
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_register_email_exists(valid_token):
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "newuser",
        "password": "testpassword",
        "email": "existing@example.com",
        "phone": "1234567890"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 409
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_register_invalid_input():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "",
        "password": "testpassword",
        "email": "invalidemail",
        "phone": "1234567890"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_register_missing_required_fields():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data