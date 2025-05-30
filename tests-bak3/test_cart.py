import pytest
import requests

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3NhbiIsImV4cCI6MTc0ODUzMzUwMH0.ZZMtygkm-99Zn3mpBFmyzAUkxYirLx-BqZlbMnKjE5U"

@pytest.mark.api
class TestCartAPI:
    def test_get_cart_success(self):
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/cart", headers=headers)
        assert response.status_code == 200
        assert "items" in response.json()

    def test_get_cart_missing_authorization(self):
        response = requests.get(f"{BASE_URL}/cart")
        assert response.status_code == 422
        assert "detail" in response.json()