import requests
import json
import time

def test_ollama():
    base_url = "http://localhost:11434"
    try:
        # 测试连接
        print("测试Ollama连接...")
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        print(f"模型列表状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"可用模型: {[model['name'] for model in models.get('models', [])]}")
        else:
            print(f"模型列表响应: {response.text}")
            return False

        # 测试生成
        print("\n测试模型生成...")
        payload = {
            "model": "llama3.1",
            "prompt": "请用一句话回答：什么是人工智能？",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=60)
        end_time = time.time()
        
        print(f"生成状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"生成响应时间: {end_time - start_time:.2f}秒")
            print(f"回答: {result.get('response', '无回答')}")
            return True
        else:
            print(f"生成错误: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到Ollama服务，请确保Ollama正在运行")
        return False
    except requests.exceptions.Timeout:
        print("错误: 请求超时，Ollama服务响应过慢")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    exit(0 if success else 1)