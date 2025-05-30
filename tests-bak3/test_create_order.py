import pytest
import requests

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3NhbiIsImV4cCI6MTc0ODUzMzUwMH0.ZZMtygkm-99Zn3mpBFmyzAUkxYirLx-BqZlbMnKjE5U"

@pytest.mark.api
class TestCreateOrderAPI:
    @pytest.fixture
    def valid_payload(self):
        return {
            "address_id": 1
        }

    def test_create_order_success(self, valid_payload):
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.post(f"{BASE_URL}/orders/create", json=valid_payload, headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_create_order_missing_required_field(self):
        payload = {"address_id": None}
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.post(f"{BASE_URL}/orders/create", json=payload, headers=headers)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_order_missing_authorization(self, valid_payload):
        response = requests.post(f"{BASE_URL}/orders/create", json=valid_payload)
        assert response.status_code == 422
        assert "detail" in response.json()