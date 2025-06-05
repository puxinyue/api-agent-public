import requests
import os


async def save_script_to_file(filename: str, code: str):
    """
    将Python代码保存到项目根目录下的tests文件夹。
    :param filename: 要保存的文件名（包括.py扩展名）
    :param code: 要保存的Python代码（字符串形式）
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    tests_dir = os.path.join(root_dir, 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    name, ext = os.path.splitext(os.path.basename(filename))
    final_path = os.path.join(tests_dir, filename)
    counter = 1
    # 防止重名
    while os.path.exists(final_path):
        new_name = f"{name}_{counter}{ext}"
        final_path = os.path.join(tests_dir, new_name)
        counter += 1
    try:
        with open(final_path, 'w', encoding='utf-8') as file:
            file.write(code)
        print(f"代码已成功保存到 {final_path}")
        return "FINISHED"
    except Exception as e:
        print(f"保存文件时出错: {e}")

async def load_api_doc():
    """加载API描述文档"""
    res = requests.get("http://127.0.0.1:5500/openapi.json")
    return res.json()
