import asyncio
from agent import Agent, Team, Termination, Console
from . import tools
from . import llms
import json
from agent.tools import load_api_doc, save_script_to_file
from agent.llms import model_client
from autogen_core.models import UserMessage
import re
import os
import yaml


# 接口自动化测试脚本生成提示词
prompt = """
 你是一个专业的接口自动化测试专家，擅长根据 API 接口描述生成测试用例。现在我将提供一份基于 FastAPI 生成的 JSON 接口描述（OpenAPI/Swagger 格式），你的任务是根据这份 JSON 描述生成全面的接口测试用例，特别关注以下场景和要求：

 BASE_URL = "http://localhost:8000"
 
### 测试场景
1. **必填参数校验**：特别关注测试所有必填字段的正常情况、缺失必填字段、必填字段为空或无效值的情况。
   - 对 OpenAPI 中标记为 required 的所有字段进行断言校验
   - 使用 assert 语句验证必填字段的存在性和有效性
   - 对必填字段进行类型检查：assert isinstance(response.json()["field_name"], expected_type)
   - 对必填字段进行值检查：assert response.json()["field_name"] == expected_value
   - 为每个必填字段生成以下测试用例（headers中只校验Authorization字段，不需要校验其他字段）：
     * 正常值测试：使用有效的值
     * 缺失测试：完全移除该字段
     * 空值测试：设置字段为空（如空字符串、null、0等）
     * 类型错误测试：使用错误的数据类型（如字符串代替数字）
     * 格式错误测试：使用不符合格式的值（如无效的邮箱格式）
   - 确保每个必填字段都有独立的测试用例，不要合并多个字段的测试
   - 在测试用例名称中明确标识被测试的字段（如 test_create_user_missing_username）

2. **非必填参数校验**：特别关注测试非必填字段的各种组合，包括提供非必填字段、部分提供、完全不提供的情况。

3. **边界测试**：针对参数的边界值（如字符串长度、数值范围、枚举值）生成测试用例。

4. **异常测试**：测试无效输入（如错误的数据类型、格式不匹配）以及 JSON 描述中定义的异常状态码（如 400、401、403、404、500）。

5. **正向测试**：测试正常输入下接口的正确响应。

6. **请求头（Header）校验**：只关注 `Authorization` 头（如 Bearer Token、API Key）。生成以下测试用例：
   - 使用有效的 `Authorization` 头（如正确的 Bearer Token 或 API Key）。
   - 缺失 `Authorization` 头，预期 JSON 描述中定义的认证失败状态码（如 401）。
   - 提供无效的 `Authorization` 头（如过期 Token、错误格式），预期 JSON 描述中定义的认证失败状态码（如 401 或 403）。
   - 注意：其他 headers 里的字段不需要校验，只关注 Authorization token 的校验。

7. **响应数据结构校验**：
   - **List 接口**：对于返回列表的接口，响应数据结构为 `{"data": [...]}`，断言需检查：
     - `response.json()` 是一个字典，包含 `data` 字段。
     - `response.json()["data"]` 是一个列表（使用 `assert isinstance(response.json()["data"], list)`）。
     - 如果 JSON 描述指定了 `data` 列表中元素的 Schema，验证每个元素的字段名称、类型和约束（如 `id: integer`, `email: string, format=email`）。
     - 包含空列表场景的测试用例（`assert response.json()["data"] == []`）。
   - **非 List 接口**：对于返回单个对象的接口（如 `{"order_id": int, "order_no": str, "total_amount": float}`），断言需：
     - 检查响应是一个字典（`assert isinstance(response.json(), dict)`）。
     - 验证所有 JSON 描述中定义的字段是否存在、类型正确、符合约束（如枚举值、格式、最小/最大值）。
     - 避免断言 Schema 中未定义的字段（如 `message`），除非接口描述明确要求。
     - 如果字段为可选，生成测试用例验证字段缺失时的行为，并在注释中说明。

8. **状态码断言**：
   - 状态码断言（如 `assert response.status_code == <code>`）**必须严格基于 JSON 描述中的 `responses` 字段**（如 `200`, `201`, `400`, `401`）。
   - 为 JSON 描述中定义的每种状态码生成对应的测试用例（如 200/201 表示成功，400 表示参数错误，401 表示认证失败）。
   - **禁止假设或添加 JSON 描述中未定义的状态码**（如未定义 403 时不得断言 403）。
   - 如果 JSON 描述中缺少某些场景的状态码（如认证失败未明确状态码），在注释中说明无法生成相关测试用例，并建议用户补充描述。
   - 确保状态码断言与测试场景（如正常请求、参数错误、认证失败）一致，并在断言中添加上下文（如 `"Expected status code 200 as per API spec"`）。

9. **断言错误预防**：
   - 避免断言 JSON Schema 中未定义的字段（如 `message`），确保响应字段校验严格匹配 Schema。
   - 确保状态码断言严格遵循 JSON 描述的 `responses` 字段，避免断言未定义状态码导致错误。
   - 在注释中说明断言依据（状态码和响应 Schema 来源于 JSON 描述）以及任何限制（如缺少状态码定义）。

### 输入格式
我将提供以下内容：
- **JSON 接口描述**：基于 FastAPI 的 OpenAPI/Swagger 格式，包含接口的路径、方法（GET/POST/PUT 等）、参数（路径参数、查询参数、请求体）、必填/非必填字段、数据类型、响应格式、请求头（如 `Authorization`）、状态码（`responses`）等。
- **接口描述（可选）**：可能包括接口的用途、业务逻辑或认证方式的额外说明（如 Bearer Token、API Key 的具体要求）。
- **认证信息（可选）**：如果接口需要 `Authorization` 头，我可能提供示例 Token 或 API Key；否则，假设使用 Bearer Token，并在测试代码中用占位符表示。

### 输出要求
1. **测试用例格式**：生成 Python 代码，基于 Pytest 框架，使用 `requests` 库发送 HTTP 请求。每个测试用例需包含：
   - 测试函数名称，清晰描述测试场景（如 `test_list_users_success`, `test_create_order_invalid_token`）。
   - 请求的 URL、方法、参数（包括请求体、查询参数、请求头）。
   - 包含 `Authorization` 头的测试用例需明确指定 Header（如 `{"Authorization": "Bearer <token>"}`）。
   - 预期结果（状态码、响应内容或错误信息），断言逻辑需：
     - 状态码断言：使用 `assert response.status_code == <code>`，严格基于 JSON 描述的 `responses` 字段（如 200, 201, 400, 401）。
     - 对于 `list` 接口：检查 `response.json()["data"]` 是列表，验证列表元素字段名称、类型和约束。
     - 对于非 `list` 接口：检查响应字段严格符合 JSON Schema（如 `order_id`, `order_no`），验证字段存在性、类型和约束，避免断言未定义字段（如 `message`）。
     - 使用 `assert isinstance(response.json(), dict)` 验证响应是字典。
     - 使用类型检查（如 `isinstance(response.json()["order_id"], int)`）验证字段类型。
     - 如果字段有约束（如 `enum`, `minLength`），添加相应断言。
   - 必要的注释，说明测试目的、状态码和响应 Schema 的依据，以及任何限制（如缺少状态码定义）。

2. **测试场景分类**：
   - 按接口分组，每个接口的测试用例包含正向、负向、边界、异常、认证相关、响应字段校验和状态码校验场景。
   - 特别标注必填/非必填字段、`Authorization` 头、响应字段和状态码的测试用例。

3. **输出结构**：
   - 使用 Markdown 格式，分为"测试用例概览"和"测试代码"两部分。
   - **测试用例概览**：以表格形式列出每个测试用例的名称、描述、输入（包括请求体、查询参数和 Header）、预期状态码和响应结果。
   - **测试代码**：提供完整的 Pytest 代码，包含必要的导入、认证头配置和测试函数。

4. **其他要求**：
   - 确保测试用例覆盖所有参数组合，尤其是必填/非必填字段、`Authorization` 头、响应字段和 JSON 描述中定义的状态码。
   - 如果 JSON 描述中包含参数约束（如字符串长度、枚举值、数值范围），生成对应的边界测试用例。
   - 如果 JSON 描述中未明确某些信息（如默认值、响应字段），仅基于定义的内容生成断言，避免假设未定义字段（如 `message`）或状态码。
   - 如果 JSON 描述中缺少认证失败等场景的状态码，在注释中说明无法生成相关测试用例，并建议用户补充描述。
   - 生成的代码应易于在 Pytest 中运行，包含必要的错误处理和断言。
   - 为 `Authorization` 头测试用例提供占位符（如 `TOKEN = "your_token_here"`），并在注释中说明如何替换为实际 Token。

### 输入示例
以下是一个 FastAPI 生成的 JSON 接口描述示例，包含一个 `list` 接口和一个非 `list` 接口（订单创建），均需要 `Authorization` 头：

```json
{
  "openapi": "3.0.2",
  "paths": {
    "/users": {
      "get": {
        "summary": "List all users",
        "operationId": "list_users",
        "security": [
          {
            "BearerAuth": []
          }
        ],
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "minimum": 1,
              "maximum": 100,
              "default": 10
            },
            "description": "Number of users to return"
          },
          {
            "name": "role",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "enum": ["admin", "user"]
            },
            "description": "Filter by user role"
          }
        ],
        "responses": {
          "200": {
            "description": "List of users",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": { "type": "integer" },
                          "username": { "type": "string" },
                          "email": { "type": "string", "format": "email" },
                          "role": { "type": "string", "enum": ["admin", "user"] }
                        },
                        "required": ["id", "username", "email", "role"]
                      }
                    }
                  },
                  "required": ["data"]
                }
              }
            }
          },
          "400": { "description": "Invalid input" },
          "401": { "description": "Unauthorized, missing or invalid token" }
        }
      }
    },
    "/orders": {
      "post": {
        "summary": "Create a new order",
        "operationId": "create_order",
        "security": [
          {
            "BearerAuth": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "product_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Product ID"
                  },
                  "quantity": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Order quantity"
                  },
                  "discount_code": {
                    "type": "string",
                    "maxLength": 10,
                    "description": "Discount code (optional)"
                  }
                },
                "required": ["product_id", "quantity"]
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Order created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "order_id": { "type": "integer" },
                    "order_no": { "type": "string" },
                    "total_amount": { "type": "number" }
                  },
                  "required": ["order_id", "order_no", "total_amount"]
                }
              }
            }
          },
          "400": { "description": "Invalid input" },
          "401": { "description": "Unauthorized, missing or invalid token" }
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    }
  }
}



5. 报告增强
   ```python
   @allure.severity(allure.severity_level.CRITICAL)
   @allure.description("Test user login with valid credentials")
   ```
6. readme.md使用说明

"""

# 接口需求获取智能体(pdf、数据库等)
api_acquisition_agent = Agent(
    name="api_acquisition_agent",
    model_client=llms.model_client,
    tools=[tools.load_api_doc],
    system_message="调用工具获取接口文档",
    model_client_stream=False,
)
# 测试用例生成智能体
testcase_generator_agent = Agent(
    name="testcase_generator_agent",
    model_client=llms.model_client,
    system_message=prompt,
    model_client_stream=False,
)

# 测试用例格式化智能体
testcase_format_agent = Agent(
    name="testcase_format_agent",
    model_client=llms.model_client,
    system_message="请针对 openapi.json 中的每一个接口（每个 path+method 组合），都生成一个独立的 pytest 测试脚本文件，文件名格式为 test_<接口名>.py，并输出如下格式内容：filename:{python文件名称}.py script:{python脚本内容}",
    model_client_stream=False,
)

# 测试用例输出智能体
testcase_output_agent = Agent(
    name="testcase_output_agent",
    model_client=llms.model_client,
    tools=[tools.save_script_to_file],
    system_message="调用工具将所有生成的python脚本、README（测试用例运行文档）和 requirements.txt（依赖文件）分别保存到本地文件中，只保存文件内容本身，别无其他。每个文件保存完成后输出 `FINISHED`。",
    model_client_stream=False,
)
# 终止条件
source_termination = Termination(sources=["testcase_output_agent"])

# 组件智能体团队
team = Team([api_acquisition_agent, testcase_generator_agent, testcase_format_agent, testcase_output_agent],
                           termination_condition=source_termination)

# 在生成测试用例的同时，将 Swagger JSON 文件转换为 YAML 格式
async def convert_testcase_to_yaml(testcase_data, path, method):
    # 解析测试用例代码
    test_cases = []
    code = testcase_data["code"]
    
    # 使用正则表达式匹配测试函数及其内容
    test_functions = re.finditer(r'def\s+(test_[^\s(]+)\s*\([^)]*\):(.*?)(?=def\s+test_|$)', code, re.DOTALL)
    
    for test_func in test_functions:
        test_name = test_func.group(1)
        func_content = test_func.group(2)
        
        # 解析请求信息
        request_info = {
            "name": test_name,
            "request": {
                "url": f"$url{path}",
                "method": method.upper(),
                "headers": {
                    "User-Agent": "PostmanRuntime/7.37.3"
                }
            }
        }
        
        # 解析请求参数
        params_match = re.search(r'params\s*=\s*({[^}]+})', func_content)
        if params_match:
            try:
                params_str = params_match.group(1).replace("'", '"')
                params = json.loads(params_str)
                request_info["request"]["params"] = params
            except json.JSONDecodeError:
                pass
        
        # 解析请求体
        json_match = re.search(r'payload\s*=\s*({[^}]+})', func_content)
        if json_match:
            try:
                json_str = json_match.group(1).replace("'", '"')
                json_data = json.loads(json_str)
                request_info["request"]["json"] = json_data
            except json.JSONDecodeError:
                pass
        
        # 解析认证信息
        if "valid_token" in func_content:
            request_info["request"]["headers"]["Authorization"] = "Bearer $valid_token"
        elif "invalid_token" in func_content:
            request_info["request"]["headers"]["Authorization"] = "Bearer $invalid_token"
        
        # 添加测试用例
        test_cases.append(request_info)
    
    # 如果没有找到测试用例，生成默认的正向和反向测试用例
    if not test_cases:
        positive_testcase = {
            "name": f"test_{path.strip('/').replace('/', '_')}_{method}_positive",
            "request": {
                "url": f"$url{path}",
                "method": method.upper(),
                "headers": {
                    "User-Agent": "PostmanRuntime/7.37.3",
                    "Authorization": "Bearer $valid_token"
                }
            }
        }
        
        negative_testcase = {
            "name": f"test_{path.strip('/').replace('/', '_')}_{method}_negative",
            "request": {
                "url": f"$url{path}",
                "method": method.upper(),
                "headers": {
                    "User-Agent": "PostmanRuntime/7.37.3",
                    "Authorization": "Bearer $invalid_token"
                }
            }
        }
        
        # 添加请求体和参数
        if "requestBody" in testcase_data.get("api_doc", {}).get("paths", {}).get(path, {}).get(method, {}):
            request_body = testcase_data["api_doc"]["paths"][path][method]["requestBody"]
            if "content" in request_body and "application/json" in request_body["content"]:
                schema = request_body["content"]["application/json"]["schema"]
                if "properties" in schema:
                    example_data = {}
                    for prop_name, prop_schema in schema["properties"].items():
                        if prop_schema["type"] == "string":
                            example_data[prop_name] = ""
                        elif prop_schema["type"] == "integer":
                            example_data[prop_name] = 1
                        elif prop_schema["type"] == "number":
                            example_data[prop_name] = 1.0
                        elif prop_schema["type"] == "boolean":
                            example_data[prop_name] = True
                        elif prop_schema["type"] == "array":
                            example_data[prop_name] = []
                    positive_testcase["request"]["json"] = example_data
        
        test_cases = [positive_testcase, negative_testcase]
    
    # 将测试用例转换为YAML格式
    yaml_data = yaml.dump(test_cases, default_flow_style=False, sort_keys=False)
    
    # 保存YAML文件
    swagger_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger')
    os.makedirs(swagger_dir, exist_ok=True)
    yaml_path = os.path.join(swagger_dir, f'testcase_{path.strip("/").replace("/", "_")}_{method}.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_data)

# 在 generate_testcases_for_all_endpoints 函数中调用转换函数
async def generate_testcase_with_retry(prompt, max_retries=5, delay=10):
    for attempt in range(max_retries):
        try:
            result = await testcase_generator_agent.run(task=prompt)
            content = str(result.messages[-1].content)
            return re.sub(r'(```python|```|输出文件名：.*|代码：)', '', content, flags=re.IGNORECASE).strip()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                # 每次重试后增加延迟时间
                delay *= 2
            else:
                raise e

async def generate_testcases_for_all_endpoints():
    api_doc = await load_api_doc()
    paths = api_doc["paths"]
    components = api_doc.get("components", {})
    openapi_version = api_doc.get("openapi", "3.0.0")
    info = api_doc.get("info", {})

    # 1. 生成 conftest.py（只生成一次）
    conftest_code = '''\
import pytest

BASE_URL = "http://your-api-url"  # 替换为实际API地址

@pytest.fixture(scope="session")
def valid_token():
    # Replace with actual token retrieval logic
    return "valid-token"

@pytest.fixture(scope="session")
def invalid_token():
    # Replace with actual token retrieval logic
    return "invalid-token"
'''
    tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    conftest_path = os.path.join(tests_dir, 'conftest.py')
    if not os.path.exists(conftest_path):
        with open(conftest_path, 'w', encoding='utf-8') as f:
            f.write(conftest_code)

    for path, methods in paths.items():
        for method, detail in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            # 检查请求字段数量
            request_field_count = 0
            if "requestBody" in detail:
                if "content" in detail["requestBody"] and "application/json" in detail["requestBody"]["content"]:
                    schema = detail["requestBody"]["content"]["application/json"]["schema"]
                    if "properties" in schema:
                        request_field_count += len(schema["properties"])

            # 检查响应字段数量
            response_field_count = 0
            response_schemas = {}
            for status_code, response in detail.get("responses", {}).items():
                if "content" in response and "application/json" in response["content"]:
                    schema = response["content"]["application/json"]["schema"]
                    if "properties" in schema:
                        response_field_count += len(schema["properties"])
                        response_schemas[status_code] = schema

            # 如果请求字段数量超过4个或响应字段数量超过10个，分批生成测试用例
            if request_field_count > 4 or response_field_count > 10:
                # 处理请求字段分组
                request_groups = []
                if request_field_count > 4 and "requestBody" in detail and "content" in detail["requestBody"] and "application/json" in detail["requestBody"]["content"]:
                    schema = detail["requestBody"]["content"]["application/json"]["schema"]
                    if "properties" in schema:
                        properties = schema["properties"]
                        # 按每3个字段分组
                        request_groups = [list(properties.items())[i:i + 3] for i in range(0, len(properties), 3)]

                # 处理响应字段分组
                response_groups = {}
                for status_code, schema in response_schemas.items():
                    if "properties" in schema:
                        properties = schema["properties"]
                        # 按每3个字段分组
                        response_groups[status_code] = [list(properties.items())[i:i + 3] for i in range(0, len(properties), 3)]

                # 生成测试用例
                for i in range(max(len(request_groups), max(len(groups) for groups in response_groups.values()))):
                    # 创建分组后的schema
                    group_request_schema = None
                    if request_groups and i < len(request_groups):
                        group_request_schema = {
                            "type": "object",
                            "properties": dict(request_groups[i]),
                            "required": [f[0] for f in request_groups[i] if f[0] in schema.get("required", [])]
                        }

                    # 创建分组后的响应schema
                    group_responses = {}
                    for status_code, groups in response_groups.items():
                        if i < len(groups):
                            group_responses[status_code] = {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": dict(groups[i]),
                                            "required": [f[0] for f in groups[i] if f[0] in schema.get("required", [])]
                                        }
                                    }
                                }
                            }

                    # 创建分组后的API文档
                    group_api_doc = {
                        "paths": {
                            path: {
                                method: {
                                    "responses": group_responses
                                }
                            }
                        }
                    }

                    # 添加请求体（如果有）
                    if group_request_schema:
                        group_api_doc["paths"][path][method]["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": group_request_schema
                                }
                            }
                        }

                    # 生成测试用例
                    prompt = (
                        "请为如下 openapi 接口生成pytest测试用例，只输出纯Python测试代码，不要包含文件名、注释、Markdown代码块标记。"
                        "所有用例文件开头必须加上 'from conftest import BASE_URL, valid_token, invalid_token'，"
                        "所有用到 valid_token/invalid_token 的测试函数，必须将其作为参数传入，而不是直接引用变量名。"
                        "并直接引用 BASE_URL、valid_token、invalid_token，不要在本文件定义这些变量：\n"
                        f"{json.dumps(group_api_doc, ensure_ascii=False, indent=2)}"
                    )

                    try:
                        print(f"Generating test cases for {path} {method} group {i+1}...")
                        code = await generate_testcase_with_retry(prompt)

                        # 保存测试用例
                        test_file = f"test_{path.strip('/').replace('/', '_')}_{method}_group{i+1}.py"
                        await save_script_to_file(test_file, code)
                        print(f"Successfully generated test cases for {path} {method} group {i+1}")

                        # 生成YAML
                        testcase_data = {
                            "api_doc": group_api_doc,
                            "test_name": f"test_{path.strip('/').replace('/', '_')}_{method}_group{i+1}",
                            "description": f"Test case for {method.upper()} {path} (Group {i+1})",
                            "code": code
                        }
                        await convert_testcase_to_yaml(testcase_data, path, method)

                        # 在每组之间添加延迟
                        await asyncio.sleep(5)
                    except Exception as e:
                        print(f"Error generating test cases for {path} {method} group {i+1}: {str(e)}")
                        continue
            else:
                # 字段数量较少，直接生成测试用例
                single_api_doc = {
                    "paths": {
                        path: {
                            method: {
                                "requestBody": detail.get("requestBody", {}),
                                "responses": detail.get("responses", {})
                            }
                        }
                    }
                }

                prompt = (
                    "请为如下 openapi 接口生成pytest测试用例，只输出纯Python测试代码，不要包含文件名、注释、Markdown代码块标记。"
                    "所有用例文件开头必须加上 'from conftest import BASE_URL, valid_token, invalid_token'，"
                    "所有用到 valid_token/invalid_token 的测试函数，必须将其作为参数传入，而不是直接引用变量名。"
                    "并直接引用 BASE_URL、valid_token、invalid_token，不要在本文件定义这些变量：\n"
                    f"{json.dumps(single_api_doc, ensure_ascii=False, indent=2)}"
                )

                try:
                    print(f"Generating test cases for {path} {method}...")
                    code = await generate_testcase_with_retry(prompt)
                    await save_script_to_file(f"test_{path.strip('/').replace('/', '_')}_{method}.py", code)
                    print(f"Successfully generated test cases for {path} {method}")

                    # 生成测试用例的 YAML 文件
                    testcase_data = {
                        "api_doc": single_api_doc,
                        "test_name": f"test_{path.strip('/').replace('/', '_')}_{method}",
                        "description": f"Test case for {method.upper()} {path}",
                        "code": code
                    }
                    await convert_testcase_to_yaml(testcase_data, path, method)
                except Exception as e:
                    print(f"Error generating test cases for {path} {method}: {str(e)}")
                    continue

if __name__ == "__main__":
    asyncio.run(generate_testcases_for_all_endpoints())