from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_add_to_cart_success(valid_token):
    url = f"{BASE_URL}/cart/add"
    headers = {"Authorization": valid_token}
    payload = {
        "product_id": 1,
        "quantity": 2
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_add_to_cart_insufficient_stock(valid_token):
    url = f"{BASE_URL}/cart/add"
    headers = {"Authorization": valid_token}
    payload = {
        "product_id": 1,
        "quantity": 1000
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_add_to_cart_unauthorized(invalid_token):
    url = f"{BASE_URL}/cart/add"
    headers = {"Authorization": invalid_token}
    payload = {
        "product_id": 1,
        "quantity": 2
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_add_to_cart_missing_authorization():
    url = f"{BASE_URL}/cart/add"
    payload = {
        "product_id": 1,
        "quantity": 2
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_add_to_cart_user_or_product_not_found(valid_token):
    url = f"{BASE_URL}/cart/add"
    headers = {"Authorization": valid_token}
    payload = {
        "product_id": 9999,
        "quantity": 2
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_add_to_cart_invalid_parameters(valid_token):
    url = f"{BASE_URL}/cart/add"
    headers = {"Authorization": valid_token}
    payload = {
        "product_id": "invalid",
        "quantity": "invalid"
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data