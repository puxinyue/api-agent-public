import os
import asyncio
from agent.llms import model_client
from agent import Agent

def build_yaml_prompt(pytest_code, path, method):
    prompt = f"""
你是一个接口自动化测试用例格式转换专家。请将下面的 pytest 测试用例代码，转换为 YAML 格式的接口测试用例，每个用例结构如下：
- name: <测试用例名称>
  request:
    url: $url<接口路径>
    method: <请求方法>
    headers:
      User-Agent: "PostmanRuntime/7.37.3"
      # 如有 token 也要加 Authorization
    params: # 仅 GET/DELETE 且有 params 时出现
      ...
    json:   # 仅 POST/PUT 且有 json/payload/data 时出现
      ...

请严格依照测试用例代码实际请求内容（params/json/headers）映射到 YAML，不要遗漏任何参数。不要生成多余字段。只输出 YAML 内容，不要有解释说明。

接口路径: {path}
请求方法: {method.upper()}

pytest 测试用例代码：
"""
    prompt += pytest_code
    return prompt

# 在本文件内新建AssistantAgent实例
_yaml_format_agent = Agent(
    name="yaml_format_agent",
    model_client=model_client,
    system_message="你是一个接口自动化测试用例格式转换专家。请将输入的pytest测试用例代码转换为YAML格式的接口测试用例，只输出YAML内容，不要有解释说明。",
    model_client_stream=False,
)

async def convert_testcase_to_yaml(testcase_data, path, method, group_index=None):
    code = testcase_data["code"]
    prompt = build_yaml_prompt(code, path, method)
    # 用本地新建的模型转换
    result = await _yaml_format_agent.run(task=prompt)
    # 清理大模型输出，只保留 yaml
    yaml_data = str(result.messages[-1].content)
    yaml_data = yaml_data.replace('```yaml', '').replace('```', '').strip()
    # 保存YAML文件
    swagger_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger')
    os.makedirs(swagger_dir, exist_ok=True)
    if group_index is not None:
        yaml_path = os.path.join(swagger_dir, f'testcase_{path.strip("/").replace("/", "_")}_{method}_group{group_index+1}.yaml')
    else:
        yaml_path = os.path.join(swagger_dir, f'testcase_{path.strip("/").replace("/", "_")}_{method}.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_data)

async def convert_testcase_to_yaml_with_retry(testcase_data, path, method, group_index=None, max_retries=5, delay=10):
    for attempt in range(max_retries):
        try:
            await convert_testcase_to_yaml(testcase_data, path, method, group_index)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"YAML生成失败: {path} {method} group{group_index+1 if group_index is not None else ''}，第{attempt+1}次重试，错误: {e}")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                print(f"YAML生成最终失败: {path} {method} group{group_index+1 if group_index is not None else ''}，错误: {e}") 