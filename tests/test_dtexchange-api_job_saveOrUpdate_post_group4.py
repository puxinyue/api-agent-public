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
    # mapperList 中的 type: null 字段必须为 None
    mapper_item = {
        "id": 1,
        "createTime": "2023-01-01T10:00:00Z",
        "creator": "user1",
        "editor": "user1",
        "updateTime": "2023-01-01T10:00:00Z",
        "jobId": 101,
        "sourceModelFieldId": None, # type: null
        "sourceTableName": "source_table",
        "sourceFieldName": "source_field",
        "sourceSQLFieldName": None, # type: null
        "sourceFieldDefaultValue": None, # type: null
        "sourceFieldType": "string",
        "customerFiledType": None, # type: null
        "sourceCustomerValue": None, # type: null
        "sourceFieldSeq": 1,
        "customerFiled": False,
        "targetModelFieldId": "target_model_field_id_1",
        "targetTableName": "target_table",
        "targetFieldName": "target_field",
        "targetFieldType": "string",
        "primaryKey": False,
        "partitionKey": False,
        "partitionKeySeq": 0,
        "partitionKeyType": None, # type: null
        "partitionKeyAttrs": None, # type: null
        "timePartitionConfig": None, # type: null
        "fieldProcessorConfig": None, # type: null
        "fieldProcessorConfigAttrs": None, # type: null
        "shardingKey": False,
        "columnFamily": "cf1",
        "name": "mapper_name"
    }

    return {
        "streamingMediaDTO": {"isFrameExtracting": True},
        "datasourceList": [{
            "datasourceType": {"value": "source_type_val"}, # label is not required here
            "dsTableName": "ds_table_name",
            "dsName": "datasource_name",
            "dsType": {"label": "ds_type_lbl", "value": "ds_type_val"}, # label and value required
            "metaTabId": "meta_tab_id",
            "dsConfig": { # required fields in dsConfig: writeMode, compressCodec, dataPluginType, partitionNum
                "writeMode": "overwrite",
                "compressCodec": "gzip",
                "dataPluginType": "jdbc",
                "partitionNum": 4,
                # Optional fields (not included in required list for dsConfig)
                # "codeType": {"value": "utf8"},
                # "dsConfigWayEnum": {"value": "manual"},
                # "fetchSize": 1000
            }
        }],
        "mapperList": [mapper_item] # At least one item assumed for positive test
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
                current = current.get(part)
                # 如果路径中的父级不存在或不是字典/列表，则无法设置值
                if not isinstance(current, (dict, list)):
                    raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' does not contain '{part}' or is not a dict/list.")
        elif isinstance(current, list):
            try:
                # Assuming the path refers to an item in the list, e.g., datasourceList[0].dsTableName
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
                    raise IndexError(f"List index out of range at path '{field_path}' part '{part}'")
            except (ValueError, IndexError):
                 raise ValueError(f"Invalid path for list: '{field_path}' part '{part}' is not a valid index.")
        else:
             raise ValueError(f"Invalid path: '{field_path}'. '{parts[i-1]}' is not a dict or list.")
    return data

# 辅助函数：删除嵌套字段
def delete_nested_key(data, field_path):
    """根据点分隔的路径删除嵌套字典或列表中的键"""
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
                # Assuming the path refers to an item in the list, e.g., datasourceList[0].dsTableName
                # This simplified helper assumes index 0 for list items
                index = int(part) if part.isdigit() else 0
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
                     raise IndexError(f"List index out of range at path '{field_path}' part '{part}'")
             except (ValueError, IndexError, TypeError):
                 raise ValueError(f"Invalid path for list deletion: '{field_path}'")
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


# 测试必填字符串字段允许空字符串（如果规范未限制 minLength）
# DatasourceList: dsTableName, dsName, metaTabId
# DatasourceList[*].datasourceType: value (label not required)
# DatasourceList[*].dsType: label, value
# DatasourceList[*].dsConfig: writeMode, compressCodec, dataPluginType
# MapperList: createTime, creator, editor, updateTime, sourceTableName, sourceFieldName, sourceFieldType, targetModelFieldId, targetTableName, targetFieldName, targetFieldType, columnFamily, name
# MapperList type: null fields should be None, not empty string

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
    payload["datasourceList"][0]["dsTableName"] = ""
    payload["datasourceList"][0]["dsName"] = ""
    payload["datasourceList"][0]["metaTabId"] = ""
    payload["datasourceList"][0]["datasourceType"]["value"] = ""
    payload["datasourceList"][0]["dsType"]["label"] = ""
    payload["datasourceList"][0]["dsType"]["value"] = ""
    payload["datasourceList"][0]["dsConfig"]["writeMode"] = ""
    payload["datasourceList"][0]["dsConfig"]["compressCodec"] = ""
    payload["datasourceList"][0]["dsConfig"]["dataPluginType"] = ""

    payload["mapperList"][0]["createTime"] = ""
    payload["mapperList"][0]["creator"] = ""
    payload["mapperList"][0]["editor"] = ""
    payload["mapperList"][0]["updateTime"] = ""
    payload["mapperList"][0]["sourceTableName"] = ""
    payload["mapperList"][0]["sourceFieldName"] = ""
    payload["mapperList"][0]["sourceFieldType"] = ""
    payload["mapperList"][0]["targetModelFieldId"] = "" # string
    payload["mapperList"][0]["targetTableName"] = ""
    payload["mapperList"][0]["targetFieldName"] = ""
    payload["mapperList"][0]["targetFieldType"] = ""
    payload["mapperList"][0]["columnFamily"] = ""
    payload["mapperList"][0]["name"] = ""

    # fields with type: null should remain None, not set to ""

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


def test_save_or_update_job_success_false_booleans_and_zeros(valid_token):
    """
    测试保存或更新作业接口 - 必填 boolean 参数为 false, 必填 integer 参数为 0，使用有效 token
    预期：成功，根据常见实践状态码为 200 或 201。响应为 JSON 字典（如果成功）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()

    # Set boolean and integer required fields to False/0
    payload["streamingMediaDTO"]["isFrameExtracting"] = False

    payload["datasourceList"][0]["dsConfig"]["partitionNum"] = 0

    payload["mapperList"][0]["id"] = 0
    payload["mapperList"][0]["jobId"] = 0
    payload["mapperList"][0]["sourceFieldSeq"] = 0
    payload["mapperList"][0]["customerFiled"] = False
    payload["mapperList"][0]["primaryKey"] = False
    payload["mapperList"][0]["partitionKey"] = False
    payload["mapperList"][0]["partitionKeySeq"] = 0
    payload["mapperList"][0]["shardingKey"] = False

    response = requests.post(ENDPOINT, headers=headers, json=payload)

    # 状态码断言基于常见实践，非 OpenAPI 规范定义
    assert response.status_code in [200, 201], f"预期状态码 200 或 201，实际是 {response.status_code}"
    # 响应体结构断言基于常见实践，非 OpenAPI 规范定义
    assert isinstance(response.json(), dict), "预期响应体是 JSON 字典"
    # 无法验证响应体具体字段，因 OpenAPI 规范未定义响应 Schema


# --- 必填参数缺失校验测试 (负向) ---

# 必填字段路径列表
REQUIRED_FIELDS = [
    "streamingMediaDTO", # top level object
    "datasourceList",    # top level array
    "mapperList",        # top level array

    "streamingMediaDTO.isFrameExtracting", # nested boolean

    "datasourceList[0].datasourceType", # nested object in array item
    "datasourceList[0].dsTableName",    # nested string in array item
    "datasourceList[0].dsName",         # nested string in array item
    "datasourceList[0].dsType",         # nested object in array item
    "datasourceList[0].metaTabId",      # nested string in array item
    "datasourceList[0].dsConfig",       # nested object in array item

    "datasourceList[0].datasourceType.value", # nested string in nested object
    "datasourceList[0].dsType.label",         # nested string in nested object
    "datasourceList[0].dsType.value",         # nested string in nested object

    "datasourceList[0].dsConfig.writeMode",    # nested string in nested object
    "datasourceList[0].dsConfig.compressCodec",# nested string in nested object
    "datasourceList[0].dsConfig.dataPluginType", # nested string in nested object
    "datasourceList[0].dsConfig.partitionNum", # nested integer in nested object

    # All fields in mapperList item are required
    "mapperList[0].id",                      # integer
    "mapperList[0].createTime",              # string
    "mapperList[0].creator",                 # string
    "mapperList[0].editor",                  # string
    "mapperList[0].updateTime",              # string
    "mapperList[0].jobId",                   # integer
    "mapperList[0].sourceModelFieldId",      # null
    "mapperList[0].sourceTableName",         # string
    "mapperList[0].sourceFieldName",         # string
    "mapperList[0].sourceSQLFieldName",      # null
    "mapperList[0].sourceFieldDefaultValue", # null
    "mapperList[0].sourceFieldType",         # string
    "mapperList[0].customerFiledType",       # null
    "mapperList[0].sourceCustomerValue",     # null
    "mapperList[0].sourceFieldSeq",          # integer
    "mapperList[0].customerFiled",           # boolean
    "mapperList[0].targetModelFieldId",      # string
    "mapperList[0].targetTableName",         # string
    "mapperList[0].targetFieldName",         # string
    "mapperList[0].targetFieldType",         # string
    "mapperList[0].primaryKey",              # boolean
    "mapperList[0].partitionKey",            # boolean
    "mapperList[0].partitionKeySeq",         # integer
    "mapperList[0].partitionKeyType",        # null
    "mapperList[0].partitionKeyAttrs",       # null
    "mapperList[0].timePartitionConfig",     # null
    "mapperList[0].fieldProcessorConfig",    # null
    "mapperList[0].fieldProcessorConfigAttrs",# null
    "mapperList[0].shardingKey",             # boolean
    "mapperList[0].columnFamily",            # string
    "mapperList[0].name",                    # string
]


@pytest.mark.parametrize("missing_field_path", REQUIRED_FIELDS)
def test_save_or_update_job_missing_required_field(valid_token, missing_field_path):
    """
    测试保存或更新作业接口 - 缺少必填参数
    测试每个必填字段（包括嵌套字段）缺失的情况。
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    此测试假设 datasourceList 和 mapperList 至少有一个元素用于测试其内部元素的必填字段缺失。
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

# 定义字段路径及其无效值列表
INVALID_VALUE_TESTS = [
    # Top level incorrect types
    ("streamingMediaDTO", "not_an_object"),      # object
    ("streamingMediaDTO", 123),
    ("streamingMediaDTO", []),
    ("streamingMediaDTO", None),                 # required object cannot be null

    ("datasourceList", "not_an_array"),          # array
    ("datasourceList", {}),
    ("datasourceList", None),                    # required array cannot be null
    ("datasourceList", [{"invalid_key": "value"}]), # array item missing required fields (tested separately, but type here)
    ("datasourceList", ["not_an_object_in_array"]), # array item incorrect type

    ("mapperList", "not_an_array"),              # array
    ("mapperList", 123),
    ("mapperList", None),                        # required array cannot be null
    ("mapperList", [{"invalid_key": "value"}]),   # array item missing required fields (tested separately)
    ("mapperList", ["not_an_object_in_array"]),  # array item incorrect type


    # Nested field incorrect types
    ("streamingMediaDTO.isFrameExtracting", "true"),  # boolean
    ("streamingMediaDTO.isFrameExtracting", 1),       # boolean
    ("streamingMediaDTO.isFrameExtracting", 0),       # boolean
    ("streamingMediaDTO.isFrameExtracting", None),    # required boolean cannot be null

    ("datasourceList[0].datasourceType", "not_an_object"), # object
    ("datasourceList[0].datasourceType", 123),
    ("datasourceList[0].datasourceType", []),
    ("datasourceList[0].datasourceType", None), # required object cannot be null

    ("datasourceList[0].dsTableName", 123),     # string
    ("datasourceList[0].dsTableName", True),
    ("datasourceList[0].dsTableName", {}),
    # ("datasourceList[0].dsTableName", None), # string allows null unless marked nullable=false, but it's required anyway

    ("datasourceList[0].dsName", 456),          # string
    ("datasourceList[0].dsName", False),

    ("datasourceList[0].dsType", "not_an_object"), # object
    ("datasourceList[0].dsType", 789),
    ("datasourceList[0].dsType", None), # required object cannot be null

    ("datasourceList[0].metaTabId", 1011),      # string
    ("datasourceList[0].metaTabId", True),

    ("datasourceList[0].dsConfig", "not_an_object"), # object
    ("datasourceList[0].dsConfig", 1213),
    ("datasourceList[0].dsConfig", None), # required object cannot be null

    # Nested in nested objects incorrect types
    ("datasourceList[0].datasourceType.value", 1415), # string
    ("datasourceList[0].datasourceType.value", None),# required string cannot be null

    ("datasourceList[0].dsType.label", 1617), # string
    ("datasourceList[0].dsType.label", None),# required string cannot be null
    ("datasourceList[0].dsType.value", 1819), # string
    ("datasourceList[0].dsType.value", None),# required string cannot be null

    ("datasourceList[0].dsConfig.writeMode", 2021), # string
    ("datasourceList[0].dsConfig.writeMode", None),# required string cannot be null
    ("datasourceList[0].dsConfig.compressCodec", 2223), # string
    ("datasourceList[0].dsConfig.compressCodec", None),# required string cannot be null
    ("datasourceList[0].dsConfig.dataPluginType", 2425), # string
    ("datasourceList[0].dsConfig.dataPluginType", None),# required string cannot be null
    ("datasourceList[0].dsConfig.partitionNum", "2627"),# integer
    ("datasourceList[0].dsConfig.partitionNum", 28.29), # integer
    ("datasourceList[0].dsConfig.partitionNum", None), # required integer cannot be null

    # MapperList item fields incorrect types / invalid values (specifically for type: null)
    ("mapperList[0].id", "not_an_int"),      # integer
    ("mapperList[0].id", 1.2),
    ("mapperList[0].id", None),              # required integer cannot be null

    ("mapperList[0].createTime", 3031),      # string
    ("mapperList[0].createTime", None),      # required string cannot be null

    ("mapperList[0].creator", 3233),         # string
    ("mapperList[0].creator", None),         # required string cannot be null

    ("mapperList[0].editor", 3435),          # string
    ("mapperList[0].editor", None),          # required string cannot be null

    ("mapperList[0].updateTime", 3637),      # string
    ("mapperList[0].updateTime", None),      # required string cannot be null

    ("mapperList[0].jobId", "not_an_int"),   # integer
    ("mapperList[0].jobId", None),           # required integer cannot be null

    ("mapperList[0].sourceModelFieldId", 123), # type: null - must be None
    ("mapperList[0].sourceModelFieldId", "not_null"),
    ("mapperList[0].sourceModelFieldId", {}),

    ("mapperList[0].sourceTableName", 3839), # string
    ("mapperList[0].sourceTableName", None), # required string cannot be null

    ("mapperList[0].sourceFieldName", 4041), # string
    ("mapperList[0].sourceFieldName", None), # required string cannot be null

    ("mapperList[0].sourceSQLFieldName", 4243), # type: null - must be None
    ("mapperList[0].sourceSQLFieldName", "not_null"),

    ("mapperList[0].sourceFieldDefaultValue", 4445), # type: null - must be None
    ("mapperList[0].sourceFieldDefaultValue", "not_null"),

    ("mapperList[0].sourceFieldType", 4647), # string
    ("mapperList[0].sourceFieldType", None), # required string cannot be null

    ("mapperList[0].customerFiledType", 4849), # type: null - must be None
    ("mapperList[0].customerFiledType", "not_null"),

    ("mapperList[0].sourceCustomerValue", 5051), # type: null - must be None
    ("mapperList[0].sourceCustomerValue", "not_null"),

    ("mapperList[0].sourceFieldSeq", "not_an_int"), # integer
    ("mapperList[0].sourceFieldSeq", None), # required integer cannot be null

    ("mapperList[0].customerFiled", "true"), # boolean
    ("mapperList[0].customerFiled", None),   # required boolean cannot be null

    ("mapperList[0].targetModelFieldId", 5253), # string
    ("mapperList[0].targetModelFieldId", None), # required string cannot be null

    ("mapperList[0].targetTableName", 5455), # string
    ("mapperList[0].targetTableName", None), # required string cannot be null

    ("mapperList[0].targetFieldName", 5657), # string
    ("mapperList[0].targetFieldName", None), # required string cannot be null

    ("mapperList[0].targetFieldType", 5859), # string
    ("mapperList[0].targetFieldType", None), # required string cannot be null

    ("mapperList[0].primaryKey", "false"), # boolean
    ("mapperList[0].primaryKey", None),    # required boolean cannot be null

    ("mapperList[0].partitionKey", "false"), # boolean
    ("mapperList[0].partitionKey", None),  # required boolean cannot be null

    ("mapperList[0].partitionKeySeq", "not_an_int"), # integer
    ("mapperList[0].partitionKeySeq", None), # required integer cannot be null

    ("mapperList[0].partitionKeyType", 6061), # type: null - must be None
    ("mapperList[0].partitionKeyType", "not_null"),

    ("mapperList[0].partitionKeyAttrs", 6263), # type: null - must be None
    ("mapperList[0].partitionKeyAttrs", "not_null"),

    ("mapperList[0].timePartitionConfig", 6465), # type: null - must be None
    ("mapperList[0].timePartitionConfig", "not_null"),

    ("mapperList[0].fieldProcessorConfig", 6667), # type: null - must be None
    ("mapperList[0].fieldProcessorConfig", "not_null"),

    ("mapperList[0].fieldProcessorConfigAttrs", 6869), # type: null - must be None
    ("mapperList[0].fieldProcessorConfigAttrs", "not_null"),

    ("mapperList[0].shardingKey", "false"), # boolean
    ("mapperList[0].shardingKey", None),    # required boolean cannot be null

    ("mapperList[0].columnFamily", 7071), # string
    ("mapperList[0].columnFamily", None), # required string cannot be null

    ("mapperList[0].name", 7273), # string
    ("mapperList[0].name", None), # required string cannot be null
]

@pytest.mark.parametrize("field_path, invalid_value", INVALID_VALUE_TESTS)
def test_save_or_update_job_invalid_type_or_value(valid_token, field_path, invalid_value):
    """
    测试保存或更新作业接口 - 必填参数类型错误或值不符合类型要求 (如 null, 非布尔值, 非对象等)
    预期：参数校验失败，根据 FastAPI 常见实践状态码为 422。响应为 JSON 字典（如果返回 JSON）。
    注意：状态码和响应体结构断言基于对常见 API 行为的假设，而非 OpenAPI 规范定义。
    此测试假设 datasourceList 和 mapperList 至少有一个元素用于测试其内部元素的类型错误。
    """
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    payload = get_valid_base_payload()
    payload_before_modify = copy.deepcopy(payload)

    try:
        # Set the invalid value based on the path
        set_nested_value(payload, field_path, invalid_value)
    except (ValueError, IndexError, TypeError) as e:
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
# 格式错误（如邮箱格式，除 type: null 外），或 404/500 等其他异常状态码，
# 因此无法生成相关测试用例并基于规范进行断言。
# 响应数据结构也未在规范中定义。所有断言均受 OpenAPI 规范不完整性的限制。