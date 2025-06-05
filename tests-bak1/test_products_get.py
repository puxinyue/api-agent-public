from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_get_products_success():
    url = f"{BASE_URL}/products"
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data and isinstance(data["data"], list)
    for item in data["data"]:
        assert isinstance(item, dict)
        assert all(key in item for key in ["product_id", "name", "description", "price", "stock", "category_id", "is_active"])
    assert "pagination" in data and isinstance(data["pagination"], dict)
    assert all(key in data["pagination"] for key in ["page", "size", "total"])

def test_get_products_with_category_id():
    url = f"{BASE_URL}/products"
    params = {"category_id": 1}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data and isinstance(data["data"], list)
    for item in data["data"]:
        assert isinstance(item, dict)
        assert all(key in item for key in ["product_id", "name", "description", "price", "stock", "category_id", "is_active"])
    assert "pagination" in data and isinstance(data["pagination"], dict)
    assert all(key in data["pagination"] for key in ["page", "size", "total"])

def test_get_products_with_pagination():
    url = f"{BASE_URL}/products"
    params = {"page": 2, "size": 5}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data and isinstance(data["data"], list)
    for item in data["data"]:
        assert isinstance(item, dict)
        assert all(key in item for key in ["product_id", "name", "description", "price", "stock", "category_id", "is_active"])
    assert "pagination" in data and isinstance(data["pagination"], dict)
    assert all(key in data["pagination"] for key in ["page", "size", "total"])

def test_get_products_with_invalid_category_id():
    url = f"{BASE_URL}/products"
    params = {"category_id": "invalid"}
    response = requests.get(url, params=params)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_get_products_with_invalid_page_size():
    url = f"{BASE_URL}/products"
    params = {"page": -1, "size": 0}
    response = requests.get(url, params=params)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data