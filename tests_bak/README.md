# API 测试说明

## 环境要求

- Python 3.11+
- pytest
- requests
- allure-pytest

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

```bash
pytest --alluredir=./allure-results
```

## 查看报告

```bash
allure serve ./allure-results
```

- uvicorn app.app:app --reload
- python -m agent.agents
- pytest tests --alluredir=allure-results
- allure serve allure-results
- 退出虚拟环境 deactivate
- source venv/bin/activate

## 测试覆盖

- 用户注册
- 用户登录
- 获取产品列表
- 获取购物车
- 添加商品到购物车
- 创建订单
