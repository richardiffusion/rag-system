#!/usr/bin/env python3
"""
详细的Ollama诊断脚本
"""

import requests
import json
import sys
import subprocess
import time

def run_command(cmd):
    """运行命令行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def diagnose_ollama():
    """诊断Ollama服务"""
    print("🔍 开始诊断Ollama服务...")
    
    # 1. 检查Ollama进程
    print("\n1. 检查Ollama进程...")
    if sys.platform == "win32":
        returncode, stdout, stderr = run_command("tasklist | findstr ollama")
    else:
        returncode, stdout, stderr = run_command("ps aux | grep ollama")
    
    if returncode == 0 and "ollama" in stdout:
        print("✅ Ollama进程正在运行")
    else:
        print("❌ Ollama进程未运行")
        print("💡 请运行: ollama serve")
        return False
    
    # 2. 检查API连接
    print("\n2. 检查API连接...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ API连接正常")
            models = response.json()
            if 'models' in models and models['models']:
                print("📚 可用模型:")
                for model in models['models']:
                    print(f"   - {model['name']} (大小: {model.get('size', '未知')})")
            else:
                print("❌ 没有找到模型")
        else:
            print(f"❌ API返回错误: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False
    
    # 3. 检查特定模型
    print("\n3. 检查llama3.1模型...")
    try:
        # 测试模型生成
        test_payload = {
            "model": "llama3.1",
            "prompt": "请回复'OK'表示你工作正常。",
            "stream": False
        }
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 模型测试成功: {result.get('response', '无响应')}")
            return True
        else:
            print(f"❌ 模型测试失败: {response.status_code}")
            print(f"   错误: {response.text}")
            
            # 尝试拉取模型
            print("\n🔄 尝试拉取llama3.1模型...")
            returncode, stdout, stderr = run_command("ollama pull llama3.1")
            if returncode == 0:
                print("✅ 模型拉取成功，请重新测试")
                # 等待模型加载
                time.sleep(5)
                return diagnose_ollama()  # 重新诊断
            else:
                print("❌ 模型拉取失败")
                print(f"   错误: {stderr}")
                return False
                
    except Exception as e:
        print(f"❌ 模型测试异常: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = diagnose_ollama()
    if success:
        print("\n🎉 Ollama诊断完成，服务正常！")
        sys.exit(0)
    else:
        print("\n💥 Ollama诊断失败，请根据上述提示解决问题。")
        sys.exit(1)