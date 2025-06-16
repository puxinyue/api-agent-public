from conftest import BASE_URL, valid_token, invalid_token
import requests
import pytest
import copy

# 注意：根据提供的 OpenAPI 描述，该接口的 'responses' 字段为空（{}）。
# 这意味着 OpenAPI 规范中没有定义任何预期状态码（如 200, 201, 400, 401, 422 等）或响应体结构。
# 以下测试用例中的状态码断言是基于对常见 API 行为的假设
# （例如，成功通常返回 200/201，参数校验失败返回 422，认证失败返回 401）。
# 如果实际接口行为与这些假设不符，需要根据实际情况调整断言。
# 此外，由于响应体结构未在规范中定义，测试用例无法对响应体内容进行详细结构或字段校验，
# 仅能断言响应是字典类型（如果返回 JSON）。强烈建议补充 OpenAPI 规范中的 responses 定义。

ENDPOINT = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"

# 辅助函数：生成一个基础的有效 payload
def get_valid_base_payload():
    """生成一个包含所有必填字段的基础有效 payload"""
    return {
        "filterRuleList": ["rule1", "rule2"], # 必填，字符串数组
        "jobSyncType": {"label": "sync_label", "value": "sync_value"}, # 必填对象，嵌套字段必填
        "jobExecMode": {"label": "exec_label", "value": "exec_value"}  # 必填对象，嵌套字段必填
    }

# --- 正向测试 ---

def test_save_or_update_job_success(valid_token):
    """
    测试保存或更新作业接口 - 所有必填参数正确，使用有效 token
    必填参数: filterRuleList (array of string), jobSyncType (object), jobExecMode (object)
    嵌套必填: jobSyncType.label (string), jobSyncType.value (string), jobExecMode.label (string), jobExecMode.value (string)
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_empty_array_and_strings(valid_token):
    """
    测试保存或更新作业接口 - filterRuleList 为空数组 []，必填字符串参数为空字符串，使用有效 token
    根据 OpenAPI 规范，空数组是合法的数组，string 类型没有 minLength 限制时，空字符串应被接受。
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "filterRuleList": [], # 必填数组为空数组
        "jobSyncType": {"label": "", "value": ""}, # 嵌套必填字符串为空字符串
        "jobExecMode": {"label": "", "value": ""}  # 嵌套必填字符串为空字符串
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_array_with_empty_strings(valid_token):
    """
    测试保存或更新作业接口 - filterRuleList 包含空字符串，使用有效 token
    根据 OpenAPI 规范，filterRuleList 是 string 数组，空字符串是合法的字符串。
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "filterRuleList": ["", "rule2", ""], # 必填数组包含空字符串
        "jobSyncType": {"label": "sync_label", "value": "sync_value"},
        "jobExecMode": {"label": "exec_label", "value": "exec_value"}
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# --- 必填参数缺失校验测试 (负向) ---

# 必填字段路径列表
REQUIRED_FIELDS = [
    "filterRuleList",    # array
    "jobSyncType",       # object
    "jobExecMode",       # object

    "jobSyncType.label", # string (nested)
    "jobSyncType.value", # string (nested)
    "jobExecMode.label", # string (nested)
    "jobExecMode.value", # string (nested)
]

# 辅助函数：删除嵌套字段 (从之前的任务复制，适用于字典和数组项)
def delete_nested_key(data, field_path):
    """根据点分隔的路径删除嵌套字典中的键"""
    parts = field_path.split('.')
    current = data
    for i, part in enumerate(parts):
        if isinstance(current, dict):
            if i == len(parts) - 1:
                if part in current:
                    del current[part]
                    return data # Deletion successful
                else:
                    raise KeyError(f"Key '{part}' not found at path '{field_path}'")
            elif part in current and isinstance(current[part], (dict, list)):
                current = current[part]
            else:
                raise KeyError(f"Invalid path: Intermediate key '{part}' not found or not a dict/list at path '{field_path}'")
        # This schema doesn't require deleting from list items by key, so we only handle dict
        elif isinstance(current, list):
             raise ValueError(f"Invalid path for list deletion: '{field_path}'. Cannot delete key from a list item.")
        else:
             raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' is not a dict.")
    return data # Should not reach here if deletion successful


@pytest.mark.parametrize("missing_field_path", REQUIRED_FIELDS)
def test_save_or_update_job_missing_required_field(valid_token, missing_field_path):
    """
    测试保存或更新作业接口 - 缺少必填参数
    测试每个必填字段（包括嵌套字段）缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()
    payload_before_delete = copy.deepcopy(payload)

    try:
        # Delete the required field based on the path
        delete_nested_key(payload, missing_field_path)
    except (KeyError, ValueError, TypeError) as e:
        pytest.fail(f"Failed to prepare payload by deleting '{missing_field_path}': {e}. Original payload: {payload_before_delete}")
        return # Stop the test if payload preparation fails

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试缺少字段 '{missing_field_path}'，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# --- 必填参数类型错误或值不符合类型要求校验测试 (负向) ---

# 辅助函数：设置嵌套字段的值 (从之前的任务复制，适用于字典和数组项)
def set_nested_value(data, field_path, value):
    """根据点分隔的路径设置嵌套字典或列表中的值"""
    parts = field_path.split('.')
    current = data
    for i, part in enumerate(parts):
        if isinstance(current, dict):
            if part not in current and i < len(parts) - 1:
                # 如果中间键不存在，且不是最后一个部分，尝试创建嵌套字典
                current[part] = {}
            if i == len(parts) - 1:
                current[part] = value
            else:
                current = current.get(part)
                # 如果路径中的父级不存在或不是字典/列表，则无法设置值
                if not isinstance(current, (dict, list)):
                    raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' does not contain '{part}' or is not a dict/list.")
        elif isinstance(current, list):
            try:
                # Assuming the path refers to an item in the list, e.g., filterRuleList[0]
                # This simplified helper assumes index 0 for list items based on schema structure
                index = int(part) if part.isdigit() else 0 # Basic assumption, might need refinement for complex lists
                if index < len(current):
                    if i == len(parts) - 1:
                        current[index] = value
                    else:
                        current = current[index]
                        if not isinstance(current, (dict, list)):
                             raise ValueError(f"Invalid path: '{field_path}'. List item at index {index} does not contain '{parts[i+1]}' or is not a dict/list.")
                else:
                    # If list is empty or index out of bounds, try to append if it's the last part
                    if i == len(parts) - 1 and index == len(current):
                         current.append(value) # Allow appending if testing adding an item
                    else:
                        raise IndexError(f"List index out of range or invalid at path '{field_path}' part '{part}'")
            except (ValueError, IndexError):
                 raise ValueError(f"Invalid path for list: '{field_path}' part '{part}' is not a valid index.")
        else:
             raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' is not a dict or list.")
    return data

INVALID_VALUE_TESTS = [
    # filterRuleList (array of string)
    ("filterRuleList", "not_an_array"),   # incorrect type
    ("filterRuleList", {}),               # incorrect type
    ("filterRuleList", 123),              # incorrect type
    ("filterRuleList", None),             # required array cannot be null
    ("filterRuleList[0]", 123),           # array item incorrect type (should be string)
    ("filterRuleList[0]", True),          # array item incorrect type
    ("filterRuleList[0]", {}),            # array item incorrect type
    ("filterRuleList[0]", []),            # array item incorrect type
    ("filterRuleList[0]", None),          # array item is null (string item cannot be null)
    ("filterRuleList", ["valid", 123]),   # array contains mixed types

    # jobSyncType (object with required nested strings)
    ("jobSyncType", "not_an_object"),     # incorrect type
    ("jobSyncType", []),                  # incorrect type
    ("jobSyncType", 123),                 # incorrect type
    ("jobSyncType", None),                # required object cannot be null
    ("jobSyncType", {}),                  # empty object (missing required nested fields label, value)

    # jobSyncType.label (string)
    ("jobSyncType.label", 123),           # incorrect type
    ("jobSyncType.label", True),          # incorrect type
    ("jobSyncType.label", {}),            # incorrect type
    ("jobSyncType.label", []),            # incorrect type
    ("jobSyncType.label", None),          # required string cannot be null

    # jobSyncType.value (string)
    ("jobSyncType.value", 456),           # incorrect type
    ("jobSyncType.value", False),         # incorrect type
    ("jobSyncType.value", {}),            # incorrect type
    ("jobSyncType.value", None),          # required string cannot be null

    # jobExecMode (object with required nested strings)
    ("jobExecMode", "not_an_object"),     # incorrect type
    ("jobExecMode", []),                  # incorrect type
    ("jobExecMode", None),                # required object cannot be null
    ("jobExecMode", {}),                  # empty object (missing required nested fields label, value)

    # jobExecMode.label (string)
    ("jobExecMode.label", 789),           # incorrect type
    ("jobExecMode.label", True),          # incorrect type
    ("jobExecMode.label", None),          # required string cannot be null

    # jobExecMode.value (string)
    ("jobExecMode.value", 1011),          # incorrect type
    ("jobExecMode.value", False),         # incorrect type
    ("jobExecMode.value", None),          # required string cannot be null
]

@pytest.mark.parametrize("field_path, invalid_value", INVALID_VALUE_TESTS)
def test_save_or_update_job_invalid_type_or_value(valid_token, field_path, invalid_value):
    """
    测试保存或更新作业接口 - 必填参数类型错误或值不符合类型要求 (如 null, 非布尔值, 非对象等)
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    此测试假设 filterRuleList 至少有一个元素，jobSyncType 和 jobExecMode 是有效的对象结构以便设置嵌套字段。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    # 创建一个基础有效 payload，以便修改嵌套字段
    payload = get_valid_base_payload()
    payload_before_modify = copy.deepcopy(payload)

    try:
        # Set the invalid value based on the path
        set_nested_value(payload, field_path, invalid_value)
    except (ValueError, IndexError, TypeError, KeyError) as e:
         pytest.fail(f"Failed to prepare payload by setting '{field_path}' to '{invalid_value}': {e}. Original payload: {payload_before_modify}")
         return # Stop the test if payload preparation fails


    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试字段 '{field_path}' 使用无效值 '{invalid_value}' (类型错误/null等)，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


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
    payload = get_valid_base_payload()
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
    payload = get_valid_base_payload()
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