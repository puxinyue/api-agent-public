from conftest import BASE_URL, valid_token, invalid_token
import requests

def test_data_exchange_job_query_normal(valid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {valid_token}"
    }
    payload = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_data_exchange_job_query_missing_current(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_empty_current(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": "",
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_invalid_type_current(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": "one",
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_missing_size(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": 1,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_empty_size(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": 1,
        "size": "",
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_invalid_type_size(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": 1,
        "size": "ten",
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_missing_archfullpath(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": 1,
        "size": 10
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_empty_archfullpath(invalid_token):
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {invalid_token}"
    }
    payload = {
        "current": 1,
        "size": 10,
        "archFullPath": ""
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_data_exchange_job_query_invalid_auth_header():
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "XMLHttpRequest"
    }
    payload = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 401

def test_data_exchange_job_query_invalid_cookie_header():
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "INVALID_COOKIE",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {valid_token}"
    }
    payload = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 401

def test_data_exchange_job_query_invalid_xrequestedwith_header():
    url = f"{BASE_URL}/dtexchange-api/job/page"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "SESSION=OWNiYzI1NzQtNjdhMi00YTVjLWEwOTQtNzMyMzJmMjU2YTVh; pp-sscct=3703bf45-2469-45d8-92a7-e89e76c801a4",
        "X-Requested-With": "INVALID_X_REQUESTED_WITH",
        "Authorization": f"Bearer {valid_token}"
    }
    payload = {
        "current": 1,
        "size": 10,
        "archFullPath": "root"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 401