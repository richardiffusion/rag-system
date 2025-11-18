#!/usr/bin/env python3
"""
等待服务完全启动的脚本
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_service(max_wait=60):
    """等待服务完全启动"""
    print(f"⏳ 等待服务启动 (最多等待 {max_wait} 秒)...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 服务已启动并运行正常")
                return True
        except requests.exceptions.ConnectionError:
            if i % 5 == 0:  # 每5秒打印一次状态
                print(f"  等待中... ({i+1}/{max_wait} 秒)")
        except Exception as e:
            print(f"  检查服务时出错: {e}")
        
        time.sleep(1)
    
    print("❌ 服务启动超时")
    return False

if __name__ == "__main__":
    success = wait_for_service()
    sys.exit(0 if success else 1)