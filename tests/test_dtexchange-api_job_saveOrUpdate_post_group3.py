from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_save_or_update_job_success(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200

def test_save_or_update_job_missing_sourcedstype(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_sourcedstype_label(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_targetdstype(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_empty_targetdstype_value(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": ""
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_missing_dirtydataoutputconfig(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_isstorage_type(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {valid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": "invalid",
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400

def test_save_or_update_job_invalid_auth(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 401

def test_save_or_update_job_missing_auth():
    url = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"
    data = {
        "sourceDsType": {
            "label": "Source Label",
            "value": "Source Value"
        },
        "targetDsType": {
            "label": "Target Label",
            "value": "Target Value"
        },
        "dirtyDataOutputConfig": {
            "isStorage": True,
            "storagePath": "/path/to/storage"
        }
    }
    response = requests.post(url, json=data)
    assert response.status_code == 401