import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.mark.api
class TestRegisterAPI:
    @pytest.fixture
    def valid_payload(self):
        return {
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com",
            "phone": "1234567890"
        }

    def test_register_success(self, valid_payload):
        response = requests.post(f"{BASE_URL}/auth/register", json=valid_payload)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_register_missing_required_field(self):
        payload = {"username": "testuser", "password": "testpass"}
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_register_invalid_email(self):
        payload = {
            "username": "testuser",
            "password": "testpass",
            "email": "invalidemail",
            "phone": "1234567890"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_register_invalid_phone(self):
        payload = {
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com",
            "phone": "invalidphone"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()