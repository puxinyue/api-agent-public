from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_job_page_valid_current_size_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200

def test_job_page_missing_current(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_missing_size(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_missing_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": 10
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_empty_current(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": "",
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_empty_size(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": "",
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_empty_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": 10,
        "archFullPath": ""
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_invalid_type_current(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": "one",
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_invalid_type_size(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": "ten",
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_invalid_type_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "current": 1,
        "size": 10,
        "archFullPath": 123
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_job_page_invalid_auth(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    data = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 401

def test_job_page_missing_auth():
    url = f"{BASE_URL}/dtexchange-api/job/page"
    data = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, json=data)
    assert response.status_code == 401