import pytest

BASE_URL = "http://localhost:8000"  # 替换为实际API地址

@pytest.fixture(scope="session")
def valid_token():
    # Replace with actual token retrieval logic
    return "valid-token"

@pytest.fixture(scope="session")
def invalid_token():
    # Replace with actual token retrieval logic
    return "invalid-token"
