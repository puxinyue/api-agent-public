from agent import ChatClient
model_client = ChatClient(
    model="qwen2.5-vl-72b-instruct",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="xxxxx",
    timeout=300,
     default_parameters={
        "temperature": 0.6,
    },
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
    },
)