import pytest
import requests

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3NhbiIsImV4cCI6MTc0ODUzMzUwMH0.ZZMtygkm-99Zn3mpBFmyzAUkxYirLx-BqZlbMnKjE5U"

@pytest.mark.api
class TestAddToCartAPI:
    @pytest.fixture
    def valid_payload(self):
        return {
            "product_id": 1,
            "quantity": 2
        }

    def test_add_to_cart_success(self, valid_payload):
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.post(f"{BASE_URL}/cart/add", json=valid_payload, headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_add_to_cart_missing_required_field(self):
        payload = {"product_id": None, "quantity": 2}
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=headers)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_add_to_cart_missing_authorization(self, valid_payload):
        response = requests.post(f"{BASE_URL}/cart/add", json=valid_payload)
        assert response.status_code == 422
        assert "detail" in response.json()