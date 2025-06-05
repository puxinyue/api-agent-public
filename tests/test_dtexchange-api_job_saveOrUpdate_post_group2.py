from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_save_or_update_job_success(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "remark": "This is a test job",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200

def test_save_or_update_job_missing_jobnameen(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "remark": "This is a test job",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_jobnameen(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "",
        "remark": "This is a test job",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_remark(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_remark(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "remark": "",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_supportresume(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "remark": "This is a test job"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_supportresume_type(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "remark": "This is a test job",
        "supportResume": "invalid"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_auth(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    data = {
        "jobNameEn": "Test Job",
        "remark": "This is a test job",
        "supportResume": True
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 401

def test_save_or_update_job_missing_auth():
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    data = {
        "jobNameEn": "Test Job",
        "remark": "This is a test job",
        "supportResume": True
    }
    response = requests.post(url, json=data)
    assert response.status_code == 401