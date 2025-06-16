from conftest import BASE_URL, valid_token, invalid_token
import requests
import pytest

# 注意：根据提供的 OpenAPI 描述，该接口的 'responses' 字段为空（{}）。
# 这意味着 OpenAPI 规范中没有定义任何预期状态码（如 200, 201, 400, 401 等）或响应体结构。
# 以下测试用例中的状态码断言（如 assert response.status_code == 200）是基于对常见 API 行为的假设
# （例如，成功通常返回 200/201，参数错误返回 400/422，认证失败返回 401）。
# 如果实际接口行为与这些假设不符，需要根据实际情况调整断言。
# 此外，由于响应体结构未在规范中定义，测试用例无法对响应体内容进行详细结构或字段校验，
# 仅能断言响应是字典类型（如果返回 JSON）。强烈建议补充 OpenAPI 规范中的 responses 定义。

ENDPOINT = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"

# --- 正向测试 ---

def test_save_or_update_job_success(valid_token):
    """
    测试保存或更新作业接口 - 所有必填参数正确，使用有效 token
    必填参数: jobNameEn (string), remark (string), supportResume (boolean)
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "EnglishJobName",
        "remark": "Some remarks here",
        "supportResume": True
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_false_boolean(valid_token):
    """
    测试保存或更新作业接口 - 必填 boolean 参数为 false，使用有效 token
    必填参数: supportResume (boolean)
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "AnotherJob",
        "remark": "Another remark",
        "supportResume": False # boolean 参数为 False
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

def test_save_or_update_job_success_empty_strings(valid_token):
    """
    测试保存或更新作业接口 - 必填字符串参数为空字符串，使用有效 token
    根据 OpenAPI 规范，jobNameEn 和 remark 是 string 类型，没有 minLength 限制，故空字符串应被接受。
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "", # 必填字符串为空字符串
        "remark": "",       # 必填字符串为空字符串
        "supportResume": True
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# --- 必填参数校验测试 (负向) ---

# 必填字段: jobNameEn (string), remark (string), supportResume (boolean)

@pytest.mark.parametrize("missing_field", ["jobNameEn", "remark", "supportResume"])
def test_save_or_update_job_missing_required_field(valid_token, missing_field):
    """
    测试保存或更新作业接口 - 缺少必填参数
    测试每个必填字段缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "EnglishJobName",
        "remark": "Some remarks here",
        "supportResume": True
    }
    # 移除当前测试的必填字段
    del payload[missing_field]

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试缺少 '{missing_field}' 字段，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


@pytest.mark.parametrize("field, invalid_value", [
    ("jobNameEn", 123),     # jobNameEn 应为 string, 提供 integer
    ("jobNameEn", None),    # jobNameEn 应为 string, 提供 null
    ("remark", 456),        # remark 应为 string, 提供 integer
    ("remark", None),       # remark 应为 string, 提供 null
    ("supportResume", "true"), # supportResume 应为 boolean, 提供 string
    ("supportResume", 1),    # supportResume 应为 boolean, 提供 integer (非严格模式可能接受，但规范是 boolean)
    ("supportResume", 0),    # supportResume 应为 boolean, 提供 integer
    ("supportResume", None), # supportResume 应为 boolean, 提供 null
    ("supportResume", "")    # supportResume 应为 boolean, 提供 empty string
])
def test_save_or_update_job_invalid_type_or_value(valid_token, field, invalid_value):
    """
    测试保存或更新作业接口 - 必填参数类型错误或值不符合类型要求 (如 null, 非布尔值)
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "EnglishJobName",
        "remark": "Some remarks here",
        "supportResume": True
    }
    # 设置当前测试字段的无效值
    payload[field] = invalid_value

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试字段 '{field}' 使用无效值 '{invalid_value}' (类型错误/null等)，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# Note: 必填字符串字段 (jobNameEn, remark) 的空值 ("") 测试已包含在正向测试 test_save_or_update_job_success_empty_strings 中，
# 因为根据规范没有 minLength 约束时，空字符串是合法值。

# --- 认证（Authorization Header）校验测试 ---

def test_save_or_update_job_missing_authorization():
    """
    测试保存或更新作业接口 - 缺失 Authorization Header
    预期：认证失败，根据常见实践状态码为 401。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "EnglishJobName",
        "remark": "Some remarks here",
        "supportResume": True
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (认证失败)，非 OpenAPI 规范定义
    assert response.status_code == 401, f"测试缺失 Authorization Header，预期状态码 401，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_invalid_authorization(invalid_token):
    """
    测试保存或更新作业接口 - Authorization Header 值无效 (无效 token)
    预期：认证失败，根据常见实践状态码为 401 或 403。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {invalid_token}", # 使用无效 token
        "Content-Type": "application/json"
    }
    payload = {
        "jobNameEn": "EnglishJobName",
        "remark": "Some remarks here",
        "supportResume": True
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (认证失败)，非 OpenAPI 规范定义
    # 认证失败可能返回 401 (Unauthorized) 或 403 (Forbidden)，取决于具体实现
    assert response.status_code in [401, 403], f"测试无效 Authorization Header，预期状态码 401 或 403，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# Note: OpenAPI 规范未定义非必填参数，边界值（如长度、数值范围、枚举值），
# 格式错误（如邮箱格式），或 404/500 等其他异常状态码，因此无法生成相关测试用例并基于规范进行断言。
# 响应数据结构也未在规范中定义。所有断言均受 OpenAPI 规范不完整性的限制。