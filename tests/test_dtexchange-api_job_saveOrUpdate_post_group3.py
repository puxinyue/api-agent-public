from conftest import BASE_URL, valid_token, invalid_token
import requests
import pytest

# 注意：根据提供的 OpenAPI 描述，该接口的 'responses' 字段为空（{}）。
# 这意味着 OpenAPI 规范中没有定义任何预期状态码（如 200, 201, 400, 401, 422 等）或响应体结构。
# 以下测试用例中的状态码断言是基于对常见 API 行为的假设
# （例如，成功通常返回 200/201，参数校验失败返回 422，认证失败返回 401）。
# 如果实际接口行为与这些假设不符，需要根据实际情况调整断言。
# 此外，由于响应体结构未在规范中定义，测试用例无法对响应体内容进行详细结构或字段校验，
# 仅能断言响应是字典类型（如果返回 JSON）。强烈建议补充 OpenAPI 规范中的 responses 定义。

ENDPOINT = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"

# --- 正向测试 ---

def test_save_or_update_job_success(valid_token):
    """
    测试保存或更新作业接口 - 所有必填参数正确，使用有效 token
    必填顶级参数: sourceDsType (object), targetDsType (object), dirtyDataOutputConfig (object)
    必填嵌套参数:
    sourceDsType: label (string), value (string)
    targetDsType: label (string), value (string)
    dirtyDataOutputConfig: isStorage (boolean), storagePath (string)
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_false_boolean_empty_strings(valid_token):
    """
    测试保存或更新作业接口 - 必填 boolean 参数为 false，必填字符串参数为空字符串，使用有效 token
    根据 OpenAPI 规范，string 类型没有 minLength 限制时，空字符串应被接受。boolean 可以是 True 或 False。
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sourceDsType": {"label": "", "value": ""}, # 空字符串
        "targetDsType": {"label": "TargetEmpty", "value": ""}, # 空字符串
        "dirtyDataOutputConfig": {"isStorage": False, "storagePath": ""} # boolean False, 空字符串
    }
    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# --- 必填参数校验测试 (负向) ---

# 必填顶级字段: sourceDsType, targetDsType, dirtyDataOutputConfig
@pytest.mark.parametrize("missing_field", ["sourceDsType", "targetDsType", "dirtyDataOutputConfig"])
def test_save_or_update_job_missing_top_level_required_object(valid_token, missing_field):
    """
    测试保存或更新作业接口 - 缺少顶层必填参数对象
    测试每个顶层必填字段对象缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
    }
    # 移除当前测试的必填字段对象
    del payload[missing_field]

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试缺少顶层必填对象 '{missing_field}'，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


# 必填嵌套字段
@pytest.mark.parametrize("parent_field, missing_nested_field", [
    ("sourceDsType", "label"),
    ("sourceDsType", "value"),
    ("targetDsType", "label"),
    ("targetDsType", "value"),
    ("dirtyDataOutputConfig", "isStorage"),
    ("dirtyDataOutputConfig", "storagePath"),
])
def test_save_or_update_job_missing_nested_required_field(valid_token, parent_field, missing_nested_field):
    """
    测试保存或更新作业接口 - 缺少嵌套必填参数
    测试每个嵌套必填字段缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
    }
    # 移除当前测试的嵌套必填字段
    if parent_field in payload and missing_nested_field in payload[parent_field]:
        del payload[parent_field][missing_nested_field]
    else:
        pytest.fail(f"payload 结构错误，找不到字段 {parent_field}.{missing_nested_field}")

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试缺少嵌套必填字段 '{parent_field}.{missing_nested_field}'，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


# 必填字段类型错误或值不符合类型要求 (如 null for non-nullable)
@pytest.mark.parametrize("field_path, invalid_value", [
    # 顶层对象类型错误
    ("sourceDsType", "not_an_object"),
    ("sourceDsType", 123),
    ("sourceDsType", None), # 对象也不能为 None
    ("targetDsType", []),
    ("targetDsType", None),
    ("dirtyDataOutputConfig", 123.45),
    ("dirtyDataOutputConfig", None),

    # 嵌套字符串类型错误或 null
    ("sourceDsType.label", 123),
    ("sourceDsType.label", True),
    ("sourceDsType.label", None),
    ("sourceDsType.value", 456),
    ("sourceDsType.value", False),
    ("sourceDsType.value", None),
    ("targetDsType.label", {"key": "value"}),
    ("targetDsType.label", None),
    ("targetDsType.value", []),
    ("targetDsType.value", None),
    ("dirtyDataOutputConfig.storagePath", 789),
    ("dirtyDataOutputConfig.storagePath", True),
    ("dirtyDataOutputConfig.storagePath", None),

    # 嵌套 boolean 类型错误或 null
    ("dirtyDataOutputConfig.isStorage", "true"),
    ("dirtyDataOutputConfig.isStorage", 1), # 整数 1 可能被接受为 True，取决于实现，但规范要求 boolean
    ("dirtyDataOutputConfig.isStorage", 0), # 整数 0 可能被接受为 False
    ("dirtyDataOutputConfig.isStorage", "false"),
    ("dirtyDataOutputConfig.isStorage", None), # 必填 boolean 不能为 null
    ("dirtyDataOutputConfig.isStorage", ""),    # 必填 boolean 不能为空字符串
])
def test_save_or_update_job_invalid_type_or_value(valid_token, field_path, invalid_value):
    """
    测试保存或更新作业接口 - 必填参数类型错误或值不符合类型要求 (如 null, 非布尔值, 非对象)
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    # 基础有效 payload
    payload = {
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
    }

    # 根据 field_path 设置无效值
    parts = field_path.split('.')
    if len(parts) == 1:
        # 顶级字段
        payload[parts[0]] = invalid_value
    elif len(parts) == 2:
        # 嵌套字段
        parent_field, nested_field = parts
        if parent_field in payload:
             # 确保父级字段存在且是字典
            if isinstance(payload[parent_field], dict):
                payload[parent_field][nested_field] = invalid_value
            else:
                # 如果父级字段本身类型错误，则整个 payload 是无效的
                payload[parent_field] = {nested_field: invalid_value} # 尝试构造，但通常会因父级类型错误先失败
        else:
            # 如果父级字段缺失，则构造一个包含无效嵌套值的父级对象，但通常会因父级缺失先失败
            payload[parent_field] = {nested_field: invalid_value}


    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试字段 '{field_path}' 使用无效值 '{invalid_value}' (类型错误/null等)，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema

# Note: 必填字符串字段 (label, value, storagePath) 的空值 ("") 测试已包含在正向测试
# test_save_or_update_job_success_false_boolean_empty_strings 中，
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
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
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
        "sourceDsType": {"label": "SourceDB", "value": "mysql"},
        "targetDsType": {"label": "TargetFile", "value": "hdfs"},
        "dirtyDataOutputConfig": {"isStorage": True, "storagePath": "/data/dirty"}
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