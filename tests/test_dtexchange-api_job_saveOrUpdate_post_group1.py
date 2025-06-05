from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_save_or_update_job_success(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": 123,
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200

def test_save_or_update_job_missing_jobcode(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_jobcode(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": "",
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_jobcode_type(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": "invalid",
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": 123,
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_archfullpath(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": 123,
        "archFullPath": "",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_jobname(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": 123,
        "archFullPath": "/path/to/archive"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_jobname(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobCode": 123,
        "archFullPath": "/path/to/archive",
        "jobName": ""
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_auth(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    data = {
        "jobCode": 123,
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 401

def test_save_or_update_job_missing_auth():
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    data = {
        "jobCode": 123,
        "archFullPath": "/path/to/archive",
        "jobName": "Test Job"
    }
    response = requests.post(url, json=data)
    assert response.status_code == 401