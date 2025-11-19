#!/usr/bin/env python3
"""
性能测试脚本
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def performance_test():
    """性能测试"""
    test_questions = [
        "简要介绍项目背景",
        "技术栈有哪些",
        "主要功能特点",
        "系统架构设计"
    ]
    
    print("📊 性能测试")
    print("=" * 60)
    
    for question in test_questions:
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/query/",
                json={"question": question, "top_k": 5},
                timeout=120
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ '{question}'")
                print(f"   时间: {end_time - start_time:.2f}秒")
                print(f"   检索文档: {len(result.get('source_documents', []))}")
                print(f"   回答长度: {len(result.get('answer', ''))}字符")
            else:
                print(f"❌ '{question}': 失败")
                
        except Exception as e:
            print(f"❌ '{question}': 异常 - {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    performance_test()