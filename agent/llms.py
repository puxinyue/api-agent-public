from agent import ChatClient
model_client = ChatClient(
    model="gemini-2.5-flash-preview-04-17",
    base_url="https://one.ocoolai.com/v1",
    api_key="",
    timeout=300,
     default_parameters={
        "temperature": 0.6,
    },
    generationConfig = { "thinkingConfig":{ "thinkingBudget": 0 }, "thinking": False},
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
    },
)