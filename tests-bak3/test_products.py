import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.mark.api
class TestProductsAPI:
    def test_get_products_success(self):
        response = requests.get(f"{BASE_URL}/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_products_with_category_id(self):
        params = {"category_id": 1}
        response = requests.get(f"{BASE_URL}/products", params=params)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_products_with_page_and_size(self):
        params = {"page": 2, "size": 5}
        response = requests.get(f"{BASE_URL}/products", params=params)
        assert response.status_code == 200
        assert isinstance(response.json(), list)