from conftest import BASE_URL, valid_token, invalid_token
import requests
import pytest
import copy
import json # Import json for jobAttrValue stringified JSON check

# API endpoint URL
URL = f"{BASE_URL}/dtexchange-api/job/saveOrUpdate"

# Base valid payload structure derived from the OpenAPI example and schema requirements
# This payload includes all required fields with valid example-like data.
# Note: The schema marks some fields with type 'null' as required.
# We include them with value 'None' in Python, which typically serializes to JSON null.
# We also correct the example payload where it deviates from schema requirements (e.g., jobAttrList items)
base_valid_payload = {
    "jobCode": 1539950205994752,
    "archFullPath": "root",
    "jobName": "wzs_mysql_hive_all",
    "jobNameEn": "wzs_mysql_hive_all",
    "remark": "wzs_mysql_hive_all",
    "supportResume": False,
    "sourceDsType": {
        "label": "MySQL", # Required
        "value": "MySQL"  # Required
    },
    "targetDsType": {
        "label": "Hive",  # Required
        "value": "Hive"   # Required
    },
    "dirtyDataOutputConfig": { # Required
        "isStorage": False, # Required
        "storagePath": "" # Required
    },
    "streamingMediaDTO": { # Required
        "isFrameExtracting": False # Required
    },
    "datasourceList": [ # Required
        { # Required item object
            "datasourceType": { # Required
                "value": "source", # Required within datasourceType
                "label": "source" # Not required within datasourceType
            },
            "dsTableName": "wzs_test_userinfo1", # Required
            "dsName": "autotest_mysql", # Required
            "dsType": { # Required
                "label": "MySQL", # Required within dsType
                "value": "MySQL"  # Required within dsType
            },
            "metaTabId": "wzs_test_userinfo1", # Required
            "databaseName": "starlink_pro", # Not required
            "dsConfig": { # Required
                "codeType": { # Not required object
                    "value": "UTF-8" # Required if codeType is present
                },
                "dsConfigWayEnum": { # Not required object
                    "value": "single_database_single_table" # Required if dsConfigWayEnum is present
                },
                "partitionNum": 1, # Required within dsConfig
                "fetchSize": 1000, # Not required within dsConfig
                "dataPluginType": "MySQL", # Required within dsConfig
                "writeMode": "append", # Required within dsConfig
                "compressCodec": "none" # Required within dsConfig
            }
        },
        { # Required item object
             "datasourceType": { # Required
                "value": "target", # Required within datasourceType
                "label": "target" # Not required within datasourceType
            },
            "dsTableName": "wzs_test_userinfo2", # Required
            "dsName": "autotest_hive", # Required
            "dsType": { # Required
                "label": "Hive", # Required within dsType
                "value": "Hive" # Required within dsType
            },
            "metaTabId": "MD_PT_e3a6dadcd671457e9ff51ea0267833bb", # Required
            "databaseName": "another_db", # Not required
            "dsConfig": { # Required
              "writeMode": "append", # Required within dsConfig
              "compressCodec": "none", # Required within dsConfig
              "dataPluginType": "Hive", # Required within dsConfig
              "partitionNum": 1 # Required within dsConfig
            }
        }
    ],
    "mapperList": [ # Required
        { # Required item object - all fields in schema properties list are marked as required
            "id": 21, "createTime": "2024-12-16 15:42:44", "creator": "admin",
            "editor": "admin", "updateTime": "2024-12-17 09:57:08", "jobId": 11,
            "sourceModelFieldId": None, # Required, type null
            "sourceTableName": "wzs_test_userinfo1", "sourceFieldName": "id",
            "sourceSQLFieldName": None, # Required, type null
            "sourceFieldDefaultValue": None, # Required, type null
            "sourceFieldType": "int",
            "customerFiledType": None, # Required, type null
            "sourceCustomerValue": None, # Required, type null
            "sourceFieldSeq": 1, "customerFiled": False,
            "targetModelFieldId": "MD_PTFa451748916034470bd935d0094408574",
            "targetTableName": "wzs_test_userinfo2", "targetFieldName": "id",
            "targetFieldType": "int", "primaryKey": True, "partitionKey": False,
            "partitionKeySeq": 0,
            "partitionKeyType": None, # Required, type null
            "partitionKeyAttrs": None, # Required, type null
            "timePartitionConfig": None, # Required, type null
            "fieldProcessorConfig": None, # Required, type null
            "fieldProcessorConfigAttrs": None, # Required, type null
            "shardingKey": False, "columnFamily": "", "name": "id"
        },
         { # Required item object
            "id": 22, "createTime": "2024-12-16 15:42:44", "creator": "admin",
            "editor": "admin", "updateTime": "2024-12-17 09:57:08", "jobId": 11,
            "sourceModelFieldId": None, "sourceTableName": "wzs_test_userinfo1",
            "sourceFieldName": "name", "sourceSQLFieldName": None,
            "sourceFieldDefaultValue": None, "sourceFieldType": "varchar",
            "customerFiledType": None, "sourceCustomerValue": None,
            "sourceFieldSeq": 2, "customerFiled": False,
            "targetModelFieldId": "MD_PTF3582a165fb764c9db06289f1dc6e274d",
            "targetTableName": "wzs_test_userinfo2", "targetFieldName": "name",
            "targetFieldType": "varchar", "primaryKey": False, "partitionKey": False,
            "partitionKeySeq": 0, "partitionKeyType": None, "partitionKeyAttrs": None,
            "timePartitionConfig": None, "fieldProcessorConfig": None,
            "fieldProcessorConfigAttrs": None, "shardingKey": False,
            "columnFamily": "", "name": "name"
        },
         { # Required item object
            "id": 23, "createTime": "2024-12-16 15:42:44", "creator": "admin",
            "editor": "admin", "updateTime": "2024-12-17 09:57:08", "jobId": 11,
            "sourceModelFieldId": None, "sourceTableName": "wzs_test_userinfo1",
            "sourceFieldName": "age", "sourceSQLFieldName": None,
            "sourceFieldDefaultValue": None, "sourceFieldType": "int",
            "customerFiledType": None, "sourceCustomerValue": None,
            "sourceFieldSeq": 3, "customerFiled": False,
            "targetModelFieldId": "MD_PTFd8fa7393308b469c8f2f906d562f2629",
            "targetTableName": "wzs_test_userinfo2", "targetFieldName": "age",
            "targetFieldType": "int", "primaryKey": False, "partitionKey": False,
            "partitionKeySeq": 0, "partitionKeyType": None, "partitionKeyAttrs": None,
            "timePartitionConfig": None, "fieldProcessorConfig": None,
            "fieldProcessorConfigAttrs": None, "shardingKey": False,
            "columnFamily": "", "name": "age"
        }
    ],
    "filterRuleList": [], # Required array
    "jobSyncType": { # Required
        "label": "^增^量^同^步", # Required
        "value": "1" # Required
    },
    "jobExecMode": { # Required
        "label": "^批^采^集", # Required
        "value": "batch" # Required
    },
    "resourceAllocation": { # Required
        "dsName": "default_yarn", # Required
        "prodQueue": "root.default", # Required
        "testQueue": "root.default", # Required
        "cores": None, # Required, type null
        "jobManagerMemory": None, # Required, type null
        "taskManagerMemory": None, # Required, type null
        "parallelism": None, # Required, type null
        "taskManagerNumber": 1, # Required, type integer
        "dsLabel": "default_yarn" # Required
    },
    "jobAttrList": [ # Required
        { # Required item object
            "jobAttrType": { # Required
                "value": 2, # Required within jobAttrType
                "label": "^作^业^属^性" # Required within jobAttrType
            },
            "jobAttrKey": "yarn.application.queue", # Required
            "jobAttrValue": '{"dsName":"default_yarn","dsLabel":"default_yarn","testQueue":"root.default","prodQueue":"root.default"}' # Required, type string
        },
        { # Required item object
             "jobAttrType": { # Required
                "value": 2, # Required within jobAttrType
                "label": "^作^业^属^性" # Required within jobAttrType
            },
            "jobAttrKey": "taskmanager.numberOfTaskSlots", # Required
             "jobAttrValue": "1" # Required, type string (corrected from example's integer)
        },
        { # Required item object
            "jobAttrType": { # Required
                "value": 1, # Required within jobAttrType
                "label": "^作^业^变^量" # Required within jobAttrType
            },
            "jobAttrKey": "some_key", # Required (missing in example, added)
            "jobAttrValue": "some_value" # Required (missing in example, added)
        }
    ],
    "enableBillingCheck": 0 # Required
}

# --- 正向测试 ---
def test_save_or_update_success(valid_token):
    """
    测试保存或更新作业接口，使用所有必填字段的有效值和有效的Authorization token。
    预期状态码为 200。
    响应结构应为一个字典 (根据API schema定义)。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    response = requests.post(URL, json=payload, headers=headers)

    # 断言状态码为 200 (根据API schema定义)
    assert response.status_code == 200, f"预期状态码 200，实际为 {response.status_code}. 响应: {response.text}"
    # 断言响应是一个字典 (根据API schema定义 for 200 response content)
    assert isinstance(response.json(), dict), f"预期响应为一个字典，实际为 {type(response.json())}"
    # 根据schema，200响应体是空的 {}，无需断言具体字段


# --- Authorization 校验测试 ---
def test_save_or_update_missing_authorization_header():
    """
    测试保存或更新作业接口，缺失Authorization header。
    预期状态码为 401 (基于API认证标准实践)。
    API schema中未明确定义认证失败的状态码，此处根据常见API行为断言401。
    """
    payload = copy.deepcopy(base_valid_payload)
    # 故意不发送 Authorization header
    headers = {}

    response = requests.post(URL, json=payload, headers=headers)

    # 断言状态码为 401 (基于常见API认证失败行为)
    # 注意: 此状态码断言基于常见实践，非严格依据提供的OpenAPI schema，
    # 提供的schema在responses中只定义了200。建议补充401/403等认证失败状态码到schema中。
    assert response.status_code == 401, f"预期状态码 401 (认证失败)，实际为 {response.status_code}. 响应: {response.text}"
    # 根据常见的认证失败响应，可能包含错误信息，但由于schema未定义，不强制断言结构。

def test_save_or_update_invalid_authorization_token(invalid_token):
    """
    测试保存或更新作业接口，使用无效的Authorization token。
    预期状态码为 401 或 403 (基于API认证标准实践)。
    此处断言为401。API schema中未明确定义认证失败的状态码。
    """
    headers = {"Authorization": f"Bearer {invalid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    response = requests.post(URL, json=payload, headers=headers)

    # 断言状态码为 401 (基于常见API认证失败行为)
    # 注意: 此状态码断言基于常见实践，非严格依据提供的OpenAPI schema，
    # 提供的schema在responses中只定义了200。建议补充401/403等认证失败状态码到schema中。
    assert response.status_code == 401, f"预期状态码 401 (认证失败)，实际为 {response.status_code}. 响应: {response.text}"
    # 根据常见的认证失败响应，可能包含错误信息，但由于schema未定义，不强制断言结构。


# --- 必填参数校验测试 (缺失字段) ---
# 生成顶层必填字段缺失的测试用例
required_top_level_fields = [
    "jobCode", "archFullPath", "jobName", "jobNameEn", "remark",
    "supportResume", "sourceDsType", "targetDsType", "dirtyDataOutputConfig",
    "streamingMediaDTO", "datasourceList", "mapperList", "filterRuleList",
    "jobSyncType", "jobExecMode", "resourceAllocation", "jobAttrList",
    "enableBillingCheck"
]

@pytest.mark.parametrize("missing_field", required_top_level_fields)
def test_save_or_update_missing_required_field(missing_field, valid_token):
    """
    测试保存或更新作业接口，缺失顶层必填字段。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)
    # 移除指定的必填字段
    if missing_field in payload:
        del payload[missing_field]

    response = requests.post(URL, json=payload, headers=headers)

    # 预期状态码 400 (Bad Request)，表示请求体数据校验失败
    # 注意: 状态码 400 是基于常见的API输入校验失败实践，非严格依据提供的OpenAPI schema。
    assert response.status_code == 400, f"缺失字段 {missing_field}: 预期状态码 400，实际为 {response.status_code}. 响应: {response.text}"
    # 可以进一步断言响应体包含错误信息，例如检查是否包含字段名，
    # 但由于schema未定义400响应结构，此处不做强制结构断言。


# 生成嵌套必填字段缺失的测试用例
# 格式: (父级字段名, 嵌套字段名或路径)
required_nested_fields = [
    ("sourceDsType", "label"), ("sourceDsType", "value"),
    ("targetDsType", "label"), ("targetDsType", "value"),
    ("dirtyDataOutputConfig", "isStorage"), ("dirtyDataOutputConfig", "storagePath"),
    ("streamingMediaDTO", "isFrameExtracting"),
    ("datasourceList", "item.datasourceType"), ("datasourceList", "item.dsTableName"),
    ("datasourceList", "item.dsName"), ("datasourceList", "item.dsType"),
    ("datasourceList", "item.metaTabId"), ("datasourceList", "item.dsConfig"),
    ("datasourceList", "item.datasourceType.value"),
    ("datasourceList", "item.dsType.label"), ("datasourceList", "item.dsType.value"),
    ("datasourceList", "item.dsConfig.writeMode"), ("datasourceList", "item.dsConfig.compressCodec"),
    ("datasourceList", "item.dsConfig.dataPluginType"), ("datasourceList", "item.dsConfig.partitionNum"),
    # Note: datasourceList.item.dsConfig.codeType/dsConfigWayEnum are not required objects,
    # but their 'value' is required IF the object is present. We test missing the 'value'.
    ("datasourceList", "item.dsConfig.codeType.value"),
    ("datasourceList", "item.dsConfig.dsConfigWayEnum.value"),

    ("mapperList", "item.id"), ("mapperList", "item.createTime"), ("mapperList", "item.creator"),
    ("mapperList", "item.editor"), ("mapperList", "item.updateTime"), ("mapperList", "item.jobId"),
    ("mapperList", "item.sourceModelFieldId"), ("mapperList", "item.sourceTableName"),
    ("mapperList", "item.sourceFieldName"), ("mapperList", "item.sourceSQLFieldName"),
    ("mapperList", "item.sourceFieldDefaultValue"), ("mapperList", "item.sourceFieldType"),
    ("mapperList", "item.customerFiledType"), ("mapperList", "item.sourceCustomerValue"),
    ("mapperList", "item.sourceFieldSeq"), ("mapperList", "item.customerFiled"),
    ("mapperList", "item.targetModelFieldId"), ("mapperList", "item.targetTableName"),
    ("mapperList", "item.targetFieldName"), ("mapperList", "item.targetFieldType"),
    ("mapperList", "item.primaryKey"), ("mapperList", "item.partitionKey"),
    ("mapperList", "item.partitionKeySeq"), ("mapperList", "item.partitionKeyType"),
    ("mapperList", "item.partitionKeyAttrs"), ("mapperList", "item.timePartitionConfig"),
    ("mapperList", "item.fieldProcessorConfig"), ("mapperList", "item.fieldProcessorConfigAttrs"),
    ("mapperList", "item.shardingKey"), ("mapperList", "item.columnFamily"), ("mapperList", "item.name"),

    ("jobSyncType", "label"), ("jobSyncType", "value"),
    ("jobExecMode", "label"), ("jobExecMode", "value"),
    ("resourceAllocation", "dsName"), ("resourceAllocation", "prodQueue"),
    ("resourceAllocation", "testQueue"), ("resourceAllocation", "cores"), # Required, type null
    ("resourceAllocation", "jobManagerMemory"), # Required, type null
    ("resourceAllocation", "taskManagerMemory"), # Required, type null
    ("resourceAllocation", "parallelism"), # Required, type null
    ("resourceAllocation", "taskManagerNumber"),
    ("resourceAllocation", "dsLabel"),
    ("jobAttrList", "item.jobAttrType"), ("jobAttrList", "item.jobAttrKey"),
    ("jobAttrList", "item.jobAttrValue"),
    ("jobAttrList", "item.jobAttrType.value"), ("jobAttrList", "item.jobAttrType.label"),
]

def remove_nested_field(data, path):
    """Helper to remove a nested field given a dot-separated path."""
    keys = path.split('.')
    current = data
    for i, key in enumerate(keys):
        if key == 'item': # Special handling for list items - targeting the first item
            if isinstance(current, list) and len(current) > 0:
                current = current[0]
            else:
                # Cannot traverse 'item' path if not a list or empty list
                return
        elif isinstance(current, dict):
            if key in current:
                if i == len(keys) - 1:
                    del current[key]
                else:
                    current = current[key]
            else:
                # Key not found
                return
        else:
            # Cannot traverse on non-dict/list
            return

@pytest.mark.parametrize("parent_field, missing_nested_field_path", required_nested_fields)
def test_save_or_update_missing_required_nested_field(parent_field, missing_nested_field_path, valid_token):
    """
    测试保存或更新作业接口，缺失嵌套必填字段。
    注意: resourceAllocation.cores/jobManagerMemory/taskManagerMemory/parallelism
    在schema中被标记为 required 且 type: null。测试移除这些字段。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    # 构建要移除的完整路径
    full_path = f"{parent_field}.{missing_nested_field_path}"
    remove_nested_field(payload, full_path)

    # Special case: if removing a required field from the first item of a list like datasourceList/mapperList
    # and the list becomes empty or the item becomes invalid, the test might behave differently.
    # For this test, we only remove from the first item if the list exists and is not empty.
    # If the list itself was the target (e.g., 'datasourceList'), it was handled by test_save_or_update_missing_required_field.
    # If the list is empty, attempting to remove from 'item' will do nothing, resulting in a passing test for a valid payload.
    # We assume the base_valid_payload has non-empty required lists where items have required fields.

    # Adjust payload if testing nested fields within empty lists (which shouldn't happen with base_valid_payload)
    # Or if testing required fields of optional nested objects like codeType/dsConfigWayEnum when the object is missing (handled implicitly).
    # Let's add a check to ensure the parent exists before attempting to remove the nested field.
    keys = parent_field.split('.')
    current = payload
    parent_exists = True
    for key in keys:
        if key in current:
            current = current[key]
        elif isinstance(current, list) and key == 'item' and len(current) > 0:
             current = current[0]
        else:
            parent_exists = False
            break

    # Only send the request if the parent path existed before attempting removal
    # This avoids sending the valid payload unintentionally if the path was wrong.
    if parent_exists:
        response = requests.post(URL, json=payload, headers=headers)
        # 预期状态码 400 (Bad Request)
        # 注意: 状态码 400 是基于常见的API输入校验失败实践，非严格依据提供的OpenAPI schema。
        assert response.status_code == 400, f"缺失嵌套字段 {full_path}: 预期状态码 400，实际为 {response.status_code}. 响应: {response.text}"
    else:
        pytest.fail(f"Attempted to remove nested field '{missing_nested_field_path}' from parent '{parent_field}', but parent path did not exist in the base payload.")


# --- 必填参数校验测试 (类型错误) ---
# 生成类型错误测试用例
# 格式: (字段路径, 错误类型的值)
type_error_cases = [
    ("jobCode", "not_an_integer"), # integer
    ("archFullPath", 123), # string
    ("jobName", 123), # string
    ("supportResume", "not_a_boolean"), # boolean
    ("sourceDsType", "not_an_object"), # object
    ("sourceDsType.label", 123), # string
    ("sourceDsType.value", 123), # string
    ("datasourceList", "not_an_array"), # array
    ("datasourceList.item.dsTableName", 123), # string
    ("datasourceList.item.dsType.label", 123), # string
    ("datasourceList.item.dsType.value", 123), # string
    ("datasourceList.item.dsConfig.partitionNum", "not_an_integer"), # integer
    ("mapperList", "not_an_array"), # array
    ("mapperList.item.id", "not_an_integer"), # integer
    ("mapperList.item.sourceFieldSeq", "not_an_integer"), # integer
    ("mapperList.item.customerFiled", "not_a_boolean"), # boolean
    ("mapperList.item.primaryKey", "not_a_boolean"), # boolean
    ("mapperList.item.partitionKey", "not_a_boolean"), # boolean
    ("mapperList.item.shardingKey", "not_a_boolean"), # boolean
    ("filterRuleList", "not_an_array"), # array (items are strings)
    ("filterRuleList", [1, 2]), # array of strings, provide array of integers
    ("filterRuleList", ["valid", 123]), # array of strings, one invalid item type
    ("jobSyncType", "not_an_object"), # object
    ("jobSyncType.label", 123), # string
    ("jobSyncType.value", 123), # string
    ("jobExecMode", "not_an_object"), # object
    ("jobExecMode.label", 123), # string
    ("jobExecMode.value", 123), # string
    ("resourceAllocation", "not_an_object"), # object
    ("resourceAllocation.taskManagerNumber", "not_an_integer"), # integer
    # Testing incorrect types for required null fields - setting non-null/incorrect type value
    ("resourceAllocation.cores", 0), # Should be null according to schema
    ("resourceAllocation.jobManagerMemory", ""), # Should be null
    ("resourceAllocation.parallelism", False), # Should be null
    ("jobAttrList", "not_an_array"), # array
    ("jobAttrList.item.jobAttrKey", 123), # string
    ("jobAttrList.item.jobAttrValue", 123), # string
    ("jobAttrList.item.jobAttrType.value", "not_an_integer"), # integer
    ("jobAttrList.item.jobAttrType.label", 123), # string
    ("enableBillingCheck", "not_an_integer"), # integer
]

def set_nested_field(data, path, value):
    """Helper to set a nested field's value given a dot-separated path."""
    keys = path.split('.')
    current = data
    for i, key in enumerate(keys):
        if key == 'item': # Special handling for list items - targeting the first item
            if isinstance(current, list) and len(current) > 0:
                current = current[0]
            else:
                 # Cannot traverse 'item' path if not a list or empty list
                return False # Indicate failure
        elif isinstance(current, dict):
             if key in current:
                if i == len(keys) - 1:
                    current[key] = value
                    return True # Indicate success
                else:
                    current = current[key]
             elif i < len(keys) - 1:
                 # Key not found in dictionary before the last step, cannot set
                 return False
             else:
                 # Last key not found, but parent exists - add the key
                 current[key] = value
                 return True
        else:
            # Cannot traverse on non-dict/list
            return False
    return False # Should not reach here for valid paths


@pytest.mark.parametrize("field_path, invalid_value", type_error_cases)
def test_save_or_update_type_error(field_path, invalid_value, valid_token):
    """
    测试保存或更新作业接口，必填字段数据类型错误。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    # Attempt to set the invalid value at the specified path
    success = set_nested_field(payload, field_path, invalid_value)

    # Only send the request if the field path was successfully set
    if success:
        response = requests.post(URL, json=payload, headers=headers)

        # 预期状态码 400 (Bad Request)
        # 注意: 状态码 400 是基于常见的API输入校验失败实践，非严格依据提供的OpenAPI schema。
        assert response.status_code == 400, f"字段 {field_path} 类型错误 ({invalid_value}): 预期状态码 400，实际为 {response.status_code}. 响应: {response.text}"
    else:
        pytest.fail(f"Attempted to set invalid value for field path '{field_path}', but path could not be traversed or set.")

# --- 必填参数校验测试 (空值/格式错误) ---
# 测试空字符串，0，空列表等必填字段的特殊值
# Schema没有定义格式 (如email, date-time)，所以不测试格式错误。
# Schema没有定义字符串长度、数值范围等边界，所以不测试基于schema的边界值。
empty_value_cases = [
    ("archFullPath", ""), # string (empty string)
    ("jobName", ""), # string (empty string)
    ("jobNameEn", ""), # string (empty string)
    ("remark", ""), # string (empty string)
    ("sourceDsType.label", ""), # string (empty string)
    ("sourceDsType.value", ""), # string (empty string)
    ("targetDsType.label", ""), # string (empty string)
    ("targetDsType.value", ""), # string (empty string)
    ("dirtyDataOutputConfig.storagePath", ""), # string (empty string) - already empty in base, test non-empty then empty? Or just test empty? Test empty as per required field check.
    ("datasourceList", []), # array (empty list)
    ("datasourceList.item.dsTableName", ""), # string (empty string)
    ("datasourceList.item.dsName", ""), # string (empty string)
    ("datasourceList.item.dsType.label", ""), # string (empty string)
    ("datasourceList.item.dsType.value", ""), # string (empty string)
    ("datasourceList.item.metaTabId", ""), # string (empty string)
    ("datasourceList.item.dsConfig.writeMode", ""), # string (empty string)
    ("datasourceList.item.dsConfig.compressCodec", ""), # string (empty string)
    ("datasourceList.item.dsConfig.dataPluginType", ""), # string (empty string)
    ("datasourceList.item.dsConfig.partitionNum", 0), # integer (zero, if schema implies positive) - Schema doesn't specify positive, 0 might be valid depending on backend logic, but test it as a potential 'empty' integer value.
    ("datasourceList.item.dsConfig.codeType.value", ""), # string (empty string), if codeType object exists
    ("datasourceList.item.dsConfig.dsConfigWayEnum.value", ""), # string (empty string), if dsConfigWayEnum object exists
    ("mapperList", []), # array (empty list)
    # mapperList item fields: string, int, boolean, null types.
    # Test empty string for string fields, None for null fields, 0 for int fields (if meaningful as empty), False for boolean (if meaningful as empty).
    ("mapperList.item.sourceTableName", ""),
    ("mapperList.item.sourceFieldName", ""),
    ("mapperList.item.sourceFieldType", ""),
    ("mapperList.item.targetModelFieldId", ""),
    ("mapperList.item.targetTableName", ""),
    ("mapperList.item.targetFieldName", ""),
    ("mapperList.item.targetFieldType", ""),
    ("mapperList.item.columnFamily", ""),
    ("mapperList.item.name", ""),
    ("mapperList.item.sourceFieldSeq", 0), # int (zero)
    ("mapperList.item.partitionKeySeq", 0), # int (zero)
    ("mapperList.item.sourceModelFieldId", None), # null type - already None in base, no change needed for this case
    ("mapperList.item.sourceSQLFieldName", None), # null type - already None in base
    ("mapperList.item.sourceFieldDefaultValue", None), # null type - already None in base
    ("mapperList.item.customerFiledType", None), # null type - already None in base
    ("mapperList.item.sourceCustomerValue", None), # null type - already None in base
    ("mapperList.item.partitionKeyType", None), # null type - already None in base
    ("mapperList.item.partitionKeyAttrs", None), # null type - already None in base
    ("mapperList.item.timePartitionConfig", None), # null type - already None in base
    ("mapperList.item.fieldProcessorConfig", None), # null type - already None in base
    ("mapperList.item.fieldProcessorConfigAttrs", None), # null type - already None in base
    ("filterRuleList", []), # array (empty list)
    ("jobSyncType.label", ""), # string (empty string)
    ("jobSyncType.value", ""), # string (empty string)
    ("jobExecMode.label", ""), # string (empty string)
    ("jobExecMode.value", ""), # string (empty string)
    ("resourceAllocation.dsName", ""), # string (empty string)
    ("resourceAllocation.prodQueue", ""), # string (empty string)
    ("resourceAllocation.testQueue", ""), # string (empty string)
    ("resourceAllocation.taskManagerNumber", 0), # integer (zero)
    ("resourceAllocation.dsLabel", ""), # string (empty string)
    ("jobAttrList", []), # array (empty list)
    ("jobAttrList.item.jobAttrKey", ""), # string (empty string)
    # jobAttrList.item.jobAttrValue is string, but can contain stringified JSON. Test empty string.
    ("jobAttrList.item.jobAttrValue", ""), # string (empty string)
    ("jobAttrList.item.jobAttrType.label", ""), # string (empty string)
    ("jobAttrList.item.jobAttrType.value", 0), # integer (zero)
    ("enableBillingCheck", 0), # integer (zero) - already 0 in base, test non-zero then 0? Just test 0.
]

@pytest.mark.parametrize("field_path, empty_value", empty_value_cases)
def test_save_or_update_empty_value(field_path, empty_value, valid_token):
    """
    测试保存或更新作业接口，必填字段设置为“空”值 (如空字符串，0，空列表)。
    注意: 对于 type: null 的字段，base_valid_payload 中已为 None，不再重复测试 None。
    这里主要测试非 null 类型的字段设置为其类型的“空”表示。
    """
    # Skip testing None for fields that are already None and required type null
    if empty_value is None and field_path in [
        "mapperList.item.sourceModelFieldId", "mapperList.item.sourceSQLFieldName",
        "mapperList.item.sourceFieldDefaultValue", "mapperList.item.customerFiledType",
        "mapperList.item.sourceCustomerValue", "mapperList.item.partitionKeyType",
        "mapperList.item.partitionKeyAttrs", "mapperList.item.timePartitionConfig",
        "mapperList.item.fieldProcessorConfig", "mapperList.item.fieldProcessorConfigAttrs",
        "resourceAllocation.cores", "resourceAllocation.jobManagerMemory",
        "resourceAllocation.taskManagerMemory", "resourceAllocation.parallelism"
    ]:
         # These are required type null and are already None in base_valid_payload
         # Testing them with None doesn't represent a change to an 'empty' state here.
         # Their 'missing' test already covers the primary required field check.
         # If backend treats None/null as invalid for a required field, the 'missing' test will catch it.
         return


    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    # Attempt to set the empty value at the specified path
    success = set_nested_field(payload, field_path, empty_value)

    if success:
        response = requests.post(URL, json=payload, headers=headers)

        # 预期状态码 400 (Bad Request) 或 200 (如果空值被接受为有效)
        # 根据API的实际校验逻辑，空值可能被拒绝 (400) 或被接受 (200)。
        # 对于严格校验，很多空值是无效的，所以先断言 400，如果实际是 200，则需要调整或分析原因。
        # 注意: 状态码 400 是基于常见的API输入校验失败实践，非严格依据提供的OpenAPI schema。
        assert response.status_code == 400, f"字段 {field_path} 空值 ({empty_value}): 预期状态码 400，实际为 {response.status_code}. 响应: {response.text}"
    else:
        # This might happen if attempting to set a value in an empty list using 'item' path, etc.
         pytest.fail(f"Attempted to set empty value for field path '{field_path}' ({empty_value}), but path could not be traversed or set.")


# --- 非必填参数测试 ---
# 仅测试 datasourceList.item.databaseName 和 datasourceList.item.dsConfig.fetchSize 作为非必填字段的代表
# 测试非必填字段存在和不存在的场景 (正常流程已覆盖存在场景)
def test_save_or_update_with_optional_fields_absent(valid_token):
    """
    测试保存或更新作业接口，非必填字段缺失。
    预期状态码为 200。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = copy.deepcopy(base_valid_payload)

    # 移除一些非必填字段
    # 例如: datasourceList item 1 的 databaseName
    if len(payload["datasourceList"]) > 0 and "databaseName" in payload["datasourceList"][0]:
        del payload["datasourceList"][0]["databaseName"]
    # 例如: datasourceList item 1 的 dsConfig.fetchSize
    if len(payload["datasourceList"]) > 0 and "dsConfig" in payload["datasourceList"][0] and "fetchSize" in payload["datasourceList"][0]["dsConfig"]:
         del payload["datasourceList"][0]["dsConfig"]["fetchSize"]
    # 例如: mapperList item 1 的一些非必填字段 (虽然schema标记required的多，但example里有些是null且required，可能还有其他非required的)
    # 根据schema，mapperList item里的字段几乎都是required。跳过mapperList的非必填字段测试，因为schema中几乎没有非必填的。
    # 检查顶层非必填字段 remark (已经在required里了), resourceAllocation里非必填的 (schema里required了一堆null...)
    # resourceAllocation里的cores/jobManagerMemory/taskManagerMemory/parallelism是required但type null，已在required tests中覆盖。

    # 示例 payload 中 remark 是必填的，resourceAllocation 中几乎所有字段都是必填的 (包括那些 type null 的)。
    # schema 中没有明确标记的非必填顶层字段。
    # datasourceList item 中的 databaseName 和 dsConfig.fetchSize 是非必填的。

    response = requests.post(URL, json=payload, headers=headers)

    # 预期状态码为 200
    assert response.status_code == 200, f"非必填字段缺失: 预期状态码 200，实际为 {response.status_code}. 响应: {response.text}"
    # 断言响应是一个字典
    assert isinstance(response.json(), dict), f"非必填字段缺失响应: 预期响应为一个字典，实际为 {type(response.json())}"


# --- 边界测试 ---
# Schema未明确定义字符串长度、数值范围、枚举值等边界。
# 无法基于Schema生成边界测试用例。
# 如果有具体边界信息，应在此处添加相应的测试。
# 例如:
# def test_save_or_update_job_name_max_length(valid_token):
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     payload = copy.deepcopy(base_valid_payload)
#     # 假设jobName最大长度为50，测试长度为51的情况
#     payload["jobName"] = "a" * 51
#     response = requests.post(URL, json=payload, headers=headers)
#     assert response.status_code == 400

# --- 响应数据结构校验 (在正向测试中已基本覆盖) ---
# 正向测试已断言状态码 200 和响应是字典 {}。
# 由于Schema未定义200响应体的具体字段，无法进行字段存在、类型或约束的详细断言。
# 如果Schema定义了响应字段，应在 test_save_or_update_success 中添加如下断言:
# response_data = response.json()
# assert "some_field" in response_data
# assert isinstance(response_data["some_field"], str) # 示例类型检查
# assert response_data["some_field"] == "expected_value" # 示例值检查 (如适用)


# --- 其他可能的异常测试 ---
# 例如，无效的JSON格式
def test_save_or_update_invalid_json(valid_token):
    """
    测试保存或更新作业接口，请求体为无效的JSON格式。
    预期状态码为 400 (Bad Request)。
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    # 发送一个非法的JSON字符串
    invalid_payload_string = '{"jobCode": 123, "archFullPath": "root", invalid_json}'

    response = requests.post(URL, data=invalid_payload_string, headers=headers)

    # 预期状态码 400 (Bad Request)，表示请求体格式错误
    # 注意: 状态码 400 是基于常见的API输入校验失败实践，非严格依据提供的OpenAPI schema。
    assert response.status_code == 400, f"无效JSON格式: 预期状态码 400，实际为 {response.status_code}. 响应: {response.text}"

# 测试发送非JSON格式的数据 (例如，纯文本或form-data)
def test_save_or_update_non_json_body(valid_token):
    """
    测试保存或更新作业接口，请求体不是预期的application/json格式。
    预期状态码为 415 (Unsupported Media Type) 或 400 (Bad Request)。常见是415。
    """
    headers = {"Authorization": f"Bearer {valid_token}", "Content-Type": "text/plain"}
    payload = "some plain text data"

    response = requests.post(URL, data=payload, headers=headers)

    # 预期状态码 415 或 400 (取决于API框架和配置)
    # FastAPI通常会返回 415 或 422 (Unprocessable Entity) / 400。415表示媒体类型不支持。
    # 注意: 此状态码断言基于常见的API行为，非严格依据提供的OpenAPI schema。
    assert response.status_code in [415, 422, 400], f"非JSON请求体: 预期状态码 415/422/400，实际为 {response.status_code}. 响应: {response.text}"