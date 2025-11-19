#!/usr/bin/env python3
"""
模型预热脚本 - 解决冷启动问题
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def warmup_model():
    """预热模型，避免第一个用户请求等待"""
    print("🔥 预热模型中...")
    
    warmup_questions = [
        "你好",
        "介绍一下你自己", 
        "简单问候",
        "测试"
    ]
    
    for i, question in enumerate(warmup_questions, 1):
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/v1/query/",
                json={"question": question, "top_k": 2},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                print(f"✅ 预热 {i}/{len(warmup_questions)}: {end_time - start_time:.2f}秒")
            else:
                print(f"❌ 预热 {i} 失败")
                
        except Exception as e:
            print(f"❌ 预热 {i} 异常: {e}")
    
    print("🎉 模型预热完成！现在用户可以享受快速响应")

if __name__ == "__main__":
    warmup_model()