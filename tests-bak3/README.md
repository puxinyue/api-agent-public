### 测试用例运行文档

#### 环境准备
- Python 3.8+
- pip install -r requirements.txt

#### 运行测试
- 使用 pytest 框架运行所有测试脚本：
```bash
pytest tests/
```
- 或者单独运行某个测试文件，例如 `test_register.py`：
```bash
pytest tests/test_register.py
```

#### 注意事项
- 在运行需要认证的接口测试之前，请确保已获取有效的 `Authorization` token 并替换 `your_token_here`。
- 根据实际情况调整 `BASE_URL` 的值以指向正确的 API 服务地址。