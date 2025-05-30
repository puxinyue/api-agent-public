from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_create_order_success(valid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": valid_token}
    payload = {
        "address_id": 1
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all(key in data for key in ["order_id", "order_no", "total_amount"])

def test_create_order_cart_empty_or_invalid_address(valid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": valid_token}
    payload = {
        "address_id": 9999
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_create_order_unauthorized(invalid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": invalid_token}
    payload = {
        "address_id": 1
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_create_order_user_not_found(valid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": valid_token}
    payload = {
        "address_id": 1
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_create_order_creation_failure(valid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": valid_token}
    payload = {
        "address_id": 1
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 500
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data

def test_create_order_validation_error(valid_token):
    url = f"{BASE_URL}/orders/create"
    headers = {"Authorization": valid_token}
    payload = {
        "address_id": "invalid"
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data, dict)
    assert "detail" in data