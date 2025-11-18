import requests
import json

def test_ollama():
    base_url = "http://localhost:11434"
    try:
        # 测试模型列表
        response = requests.get(f"{base_url}/api/tags")
        print(f"模型列表状态码: {response.status_code}")
        print(f"模型列表响应: {response.text}")

        # 测试生成
        payload = {
            "model": "llama3.1",
            "prompt": "什么是人工智能？",
            "stream": False
        }
        response = requests.post(f"{base_url}/api/generate", json=payload)
        print(f"生成状态码: {response.status_code}")
        print(f"生成响应: {response.text}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_ollama()