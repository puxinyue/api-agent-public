import pytest

BASE_URL = "http://localhost:8000"  # 替换为实际API地址

@pytest.fixture(scope="session")
def valid_token():
    # Replace with actual token retrieval logic
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3NhbiIsImV4cCI6MTc0ODYxNjE4NX0.aKv55HpCiFLUUHaKMKwOmLEet1Z_DxB-ynl_nq2qI0w"

@pytest.fixture(scope="session")
def invalid_token():
    # Replace with actual token retrieval logic
    return "invalid-token"
