import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.mark.api
class TestLoginAPI:
    @pytest.fixture
    def valid_payload(self):
        return {
            "username": "testuser",
            "password": "testpass"
        }

    def test_login_success(self, valid_payload):
        response = requests.post(f"{BASE_URL}/auth/login", json=valid_payload)
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_credentials(self):
        payload = {"username": "invaliduser", "password": "testpass"}
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_missing_required_field(self):
        payload = {"username": "testuser"}
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()