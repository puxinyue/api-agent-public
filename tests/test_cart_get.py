from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_get_cart_success(valid_token):
    url = f"{BASE_URL}/cart"
    headers = {"Authorization": valid_token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "cart_items" in data and isinstance(data["cart_items"], list)
    for item in data["cart_items"]:
        assert isinstance(item, dict)
        assert all(key in item for key in ["product_id", "name", "price", "quantity"])

def test_get_cart_unauthorized(invalid_token):
    url = f"{BASE_URL}/cart"
    headers = {"Authorization": invalid_token}
    response = requests.get(url, headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_get_cart_missing_authorization():
    url = f"{BASE_URL}/cart"
    response = requests.get(url)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_get_cart_user_not_found(valid_token):
    url = f"{BASE_URL}/cart"
    headers = {"Authorization": "invalid_token"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_get_cart_validation_error():
    url = f"{BASE_URL}/cart"
    headers = {"Authorization": "invalid_format_token"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "detail" in data