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

# 辅助函数：生成一个包含所有必填字段的基础有效 payload
def get_valid_base_payload():
    """生成一个包含所有必填字段的基础有效 payload"""
    # 注意: resourceAllocation 中的 cores, jobManagerMemory, taskManagerMemory, parallelism 为 type: null
    # 根据 OpenAPI 3.0 规范，type: null 的字段必须为 JSON null (即 Python 中的 None)
    return {
        "resourceAllocation": {
            "dsName": "resource_ds",
            "prodQueue": "prod",
            "testQueue": "test",
            "cores": None, # type: null
            "jobManagerMemory": None, # type: null
            "taskManagerMemory": None, # type: null
            "parallelism": None, # type: null
            "taskManagerNumber": 1,
            "dsLabel": "resource_label"
        },
        "jobAttrList": [ # 必填数组，至少包含一个必填结构的元素
            {
                "jobAttrType": {"value": 1, "label": "type1"}, # 嵌套对象，嵌套字段必填
                "jobAttrKey": "key1",
                "jobAttrValue": "value1"
            },
            {
                "jobAttrType": {"value": 2, "label": "type2"},
                "jobAttrKey": "key2",
                "jobAttrValue": "value2"
            }
        ],
        "enableBillingCheck": 1, # 必填 integer
        "filterRuleList": ["rule_a", "rule_b"] # 必填 array of string
    }

# 辅助函数：设置嵌套字段的值
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
                if part not in current or not isinstance(current[part], (dict, list)):
                    raise ValueError(f"Invalid path: '{field_path}'. '{part}' does not exist or is not a dict/list at level {i}.")
                current = current[part]
        elif isinstance(current, list):
            try:
                # Assuming the path refers to an item in the list, e.g., jobAttrList[0].jobAttrType
                # This simplified helper assumes index 0 for list items for setting nested properties.
                # For setting the list item itself, the part should be the index.
                index = int(part) # Must be an integer index for a list
                if index < len(current):
                    if i == len(parts) - 1:
                        current[index] = value
                    else:
                        if not isinstance(current[index], (dict, list)):
                             raise ValueError(f"Invalid path: '{field_path}'. List item at index {index} is not a dict or list at level {i}.")
                        current = current[index]
                else:
                    # Allow setting value at index if it extends the list and is the last part
                    if i == len(parts) - 1 and index == len(current):
                        current.append(value)
                        current = current[index] # Set current to the new item
                    else:
                        raise IndexError(f"List index {index} out of range at path '{field_path}' part '{part}'")
            except (ValueError, IndexError):
                 raise ValueError(f"Invalid path for list: '{field_path}' part '{part}' is not a valid integer index.")
        else:
             raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' is not a dict or list at level {i}.")
    return data

# 辅助函数：删除嵌套字段
def delete_nested_key(data, field_path):
    """根据点分隔的路径删除嵌套字典中的键。不支持删除数组中的元素或通过索引删除键。"""
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
        elif isinstance(current, list):
             try:
                # Assuming the path refers to an item *within* the list, e.g., jobAttrList[0].jobAttrKey
                # This simplified helper assumes index 0 for list items when navigating *into* them.
                index = int(part) # Must be an integer index for a list
                if index < len(current):
                    if i == len(parts) - 1:
                         # Cannot delete a key from a list item this way, need to modify the item itself
                        if isinstance(current[index], dict) and parts[-1] in current[index]:
                             del current[index][parts[-1]]
                             return data
                        else:
                             raise TypeError(f"Cannot delete key '{parts[-1]}' from list item at index {index} as it's not a dict or key not found.")
                    elif isinstance(current[index], (dict, list)):
                         current = current[index]
                    else:
                         raise ValueError(f"Invalid path: List item at index {index} is not a dict or list at path '{field_path}'")
                else:
                     raise IndexError(f"List index {index} out of range at path '{field_path}' part '{part}'")
             except (ValueError, IndexError, TypeError):
                 raise ValueError(f"Invalid path for list deletion: '{field_path}'. Deletion from list items by key/index is complex and simplified here.")
        else:
             raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' is not a dict or list.")
    return data # Should not reach here if deletion successful


# --- 正向测试 ---

def test_save_or_update_job_success(valid_token):
    """
    测试保存或更新作业接口 - 所有必填参数正确，使用有效 token
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


def test_save_or_update_job_success_with_empty_strings(valid_token):
    """
    测试保存或更新作业接口 - 必填字符串参数为空字符串，使用有效 token
    根据 OpenAPI 规范，string 类型没有 minLength 限制时，空字符串应被接受。
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()

    # 设置允许为空的必填字符串字段为空字符串
    payload["resourceAllocation"]["dsName"] = ""
    payload["resourceAllocation"]["prodQueue"] = ""
    payload["resourceAllocation"]["testQueue"] = ""
    payload["resourceAllocation"]["dsLabel"] = ""

    # Nested strings in jobAttrList items
    if payload["jobAttrList"]:
        payload["jobAttrList"][0]["jobAttrType"]["label"] = ""
        payload["jobAttrList"][0]["jobAttrKey"] = ""
        payload["jobAttrList"][0]["jobAttrValue"] = ""
    # filterRuleList allows empty strings
    payload["filterRuleList"] = ["", "rule_c", ""]

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_zero_integers_none_nulls_empty_array(valid_token):
    """
    测试保存或更新作业接口 - 必填 integer 参数为 0，必填 type: null 为 None，必填 array 为空数组 []，使用有效 token
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()

    # Set required integers to 0
    payload["resourceAllocation"]["taskManagerNumber"] = 0
    payload["enableBillingCheck"] = 0
    # Nested integer in jobAttrList item value
    if payload["jobAttrList"]:
        payload["jobAttrList"][0]["jobAttrType"]["value"] = 0

    # Set required type: null fields to None (already default in get_valid_base_payload, re-iterating for clarity)
    payload["resourceAllocation"]["cores"] = None
    payload["resourceAllocation"]["jobManagerMemory"] = None
    payload["resourceAllocation"]["taskManagerMemory"] = None
    payload["resourceAllocation"]["parallelism"] = None

    # Set required array to empty list
    payload["jobAttrList"] = [] # jobAttrList is required, empty array might be valid if items aren't required
    payload["filterRuleList"] = [] # filterRuleList is required, empty array is valid

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    # 注意：某些后端实现可能不允许 jobAttrList 为空，如果出现 422，则需要调整此测试
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


# --- 必填参数缺失校验测试 (负向) ---

# 必填字段路径列表
# Note: resourceAllocation fields with type: null are required, so testing missing them is necessary.
# Note: jobAttrList is a required array of objects, testing missing the array is necessary. Testing missing fields *within* an item assumes at least one item is sent, which is usually the case when the array itself is not missing.
REQUIRED_FIELDS = [
    "resourceAllocation", # top level object
    "resourceAllocation.dsName",
    "resourceAllocation.prodQueue",
    "resourceAllocation.testQueue",
    "resourceAllocation.cores", # type: null, required
    "resourceAllocation.jobManagerMemory", # type: null, required
    "resourceAllocation.taskManagerMemory", # type: null, required
    "resourceAllocation.parallelism", # type: null, required
    "resourceAllocation.taskManagerNumber", # integer
    "resourceAllocation.dsLabel",

    "jobAttrList", # top level array
    # Test missing fields within a jobAttrList item (assuming at least one item is sent)
    "jobAttrList[0].jobAttrType", # nested object in array item
    "jobAttrList[0].jobAttrType.value", # integer in nested object
    "jobAttrList[0].jobAttrType.label", # string in nested object
    "jobAttrList[0].jobAttrKey", # string in array item
    "jobAttrList[0].jobAttrValue", # string in array item

    "enableBillingCheck", # top level integer

    "filterRuleList", # top level array of string
]

@pytest.mark.parametrize("missing_field_path", REQUIRED_FIELDS)
def test_save_or_update_job_missing_required_field(valid_token, missing_field_path):
    """
    测试保存或更新作业接口 - 缺少必填参数
    测试每个必填字段（包括嵌套字段）缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    此测试对于嵌套在 jobAttrList 中的字段，假设 payload 中至少有一个 jobAttrList 项。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()
    payload_before_delete = copy.deepcopy(payload)

    try:
        # Delete the required field based on the path
        # Special handling for array items like 'jobAttrList[0].jobAttrType'
        parts = missing_field_path.split('.')
        if len(parts) > 1 and '[' in parts[-2] and ']' in parts[-2]:
             # It's a nested field within a list item, e.g., 'jobAttrList[0].jobAttrType'
             list_part = parts[-2]
             item_index = int(list_part.split('[')[-1].split(']')[0])
             nested_field_to_delete = parts[-1]
             list_name = list_part.split('[')[0]

             if list_name in payload and isinstance(payload[list_name], list) and item_index < len(payload[list_name]) and isinstance(payload[list_name][item_index], dict) and nested_field_to_delete in payload[list_name][item_index]:
                 del payload[list_name][item_index][nested_field_to_delete]
             elif list_name in payload and isinstance(payload[list_name], list) and item_index < len(payload[list_name]):
                  # Handle deeper nesting like jobAttrList[0].jobAttrType.value
                  nested_path_within_item = '.'.join(parts[parts.index(list_part)+1:])
                  current_item = payload[list_name][item_index]
                  delete_nested_key(current_item, nested_path_within_item)
             else:
                 raise KeyError(f"Could not find or access list item or nested field at path '{missing_field_path}'")
        else:
             # Standard nested or top-level field
             delete_nested_key(payload, missing_field_path)

    except (KeyError, ValueError, TypeError, IndexError) as e:
        pytest.fail(f"Failed to prepare payload by deleting '{missing_field_path}': {e}. Original payload: {payload_before_delete}")
        return # Stop the test if payload preparation fails

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践 (FastAPI 验证错误)，非 OpenAPI 规范定义
    assert response.status_code == 422, f"测试缺少字段 '{missing_field_path}'，预期状态码 422，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


# --- 必填参数类型错误或值不符合类型要求校验测试 (负向) ---

INVALID_VALUE_TESTS = [
    # resourceAllocation (object)
    ("resourceAllocation", "not_an_object"),
    ("resourceAllocation", []),
    ("resourceAllocation", None), # Required object cannot be null

    # resourceAllocation nested fields
    ("resourceAllocation.dsName", 123), # string
    ("resourceAllocation.dsName", None), # Required string cannot be null
    ("resourceAllocation.prodQueue", False), # string
    ("resourceAllocation.prodQueue", None), # Required string cannot be null
    ("resourceAllocation.testQueue", {}), # string
    ("resourceAllocation.testQueue", None), # Required string cannot be null

    ("resourceAllocation.cores", "not_null"), # type: null must be None
    ("resourceAllocation.cores", 1),
    ("resourceAllocation.cores", False),
    ("resourceAllocation.cores", []),
    ("resourceAllocation.cores", {}),

    ("resourceAllocation.jobManagerMemory", "not_null"), # type: null must be None
    ("resourceAllocation.jobManagerMemory", 123),
    ("resourceAllocation.taskManagerMemory", True), # type: null must be None
    ("resourceAllocation.parallelism", []), # type: null must be None

    ("resourceAllocation.taskManagerNumber", "not_an_int"), # integer
    ("resourceAllocation.taskManagerNumber", 1.2),
    ("resourceAllocation.taskManagerNumber", True),
    ("resourceAllocation.taskManagerNumber", None), # Required integer cannot be null

    ("resourceAllocation.dsLabel", 456), # string
    ("resourceAllocation.dsLabel", None), # Required string cannot be null

    # jobAttrList (array of object)
    ("jobAttrList", "not_an_array"),
    ("jobAttrList", {}),
    ("jobAttrList", None), # Required array cannot be null
    ("jobAttrList", [None]), # Array item is null (must be object)
    ("jobAttrList", ["not_an_object_item"]), # Array item incorrect type

    # jobAttrList item fields (assuming at least one item at index 0 exists)
    ("jobAttrList[0].jobAttrType", "not_an_object"), # object
    ("jobAttrList[0].jobAttrType", None), # Required object cannot be null
    ("jobAttrList[0].jobAttrType", {}), # Missing required nested fields value, label

    ("jobAttrList[0].jobAttrType.value", "not_an_int"), # integer
    ("jobAttrList[0].jobAttrType.value", 1.2),
    ("jobAttrList[0].jobAttrType.value", None), # Required integer cannot be null

    ("jobAttrList[0].jobAttrType.label", 789), # string
    ("jobAttrList[0].jobAttrType.label", None), # Required string cannot be null

    ("jobAttrList[0].jobAttrKey", 1011), # string
    ("jobAttrList[0].jobAttrKey", None), # Required string cannot be null

    ("jobAttrList[0].jobAttrValue", 1213), # string
    ("jobAttrList[0].jobAttrValue", None), # Required string cannot be null

    # enableBillingCheck (integer)
    ("enableBillingCheck", "not_an_int"),
    ("enableBillingCheck", 1.2),
    ("enableBillingCheck", True),
    ("enableBillingCheck", None), # Required integer cannot be null

    # filterRuleList (array of string)
    ("filterRuleList", "not_an_array"),
    ("filterRuleList", {}),
    ("filterRuleList", None), # Required array cannot be null
    ("filterRuleList", [123]), # Array item incorrect type (integer instead of string)
    ("filterRuleList", [True]), # Array item incorrect type
    ("filterRuleList", [{}]), # Array item incorrect type
    ("filterRuleList", [[]]), # Array item incorrect type
    ("filterRuleList", [None]), # Array item is null (string item cannot be null)
    ("filterRuleList", ["valid", 456, "another_valid"]), # Array contains mixed types

]

@pytest.mark.parametrize("field_path, invalid_value", INVALID_VALUE_TESTS)
def test_save_or_update_job_invalid_type_or_value(valid_token, field_path, invalid_value):
    """
    测试保存或更新作业接口 - 必填参数类型错误或值不符合类型要求 (如 null, 非布尔值, 非对象等)
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    此测试对于嵌套在 jobAttrList 中的字段，假设 payload 中至少有一个 jobAttrList 项。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    # 创建一个基础有效 payload，以便修改字段
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

# Note: OpenAPI 规范未定义非必填参数（除了那些明确标记 type: null 且 required 的），
# 边界值（如长度、数值范围、枚举值），格式错误（如邮箱格式），
# 或 404/500 等其他异常状态码，因此无法生成相关测试用例并基于规范进行断言。
# 响应数据结构也未在规范中定义。所有断言均受 OpenAPI 规范不完整性的限制。