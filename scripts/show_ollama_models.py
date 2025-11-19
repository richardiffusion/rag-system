#!/usr/bin/env python3
"""
简单的Ollama健康检查脚本
"""

import requests
import sys

def check_ollama():
    """检查Ollama服务状态"""
    try:
        print("检查Ollama服务...")
        
        # 测试连接
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama服务正在运行")
            
            # 显示可用模型
            models = response.json()
            if 'models' in models and models['models']:
                print("📚 可用模型:")
                for model in models['models']:
                    print(f"  - {model['name']}")
            else:
                print("❌ 没有找到模型，请使用 'ollama pull llama3.1' 下载模型")
                
            return True
        else:
            print(f"❌ Ollama服务返回错误状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务")
        print("💡 请确保Ollama服务正在运行:")
        print("   1. 打开新的终端窗口")
        print("   2. 运行: ollama serve")
        print("   3. 保持终端窗口打开")
        return False
        
    except Exception as e:
        print(f"❌ 检查Ollama时出错: {e}")
        return False

if __name__ == "__main__":
    if check_ollama():
        sys.exit(0)
    else:
        sys.exit(1)