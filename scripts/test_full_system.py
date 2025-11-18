#!/usr/bin/env python3
"""
完整系统测试脚本 - 修复版
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def wait_for_service():
    """等待服务启动"""
    print("⏳ 等待服务启动...")
    for i in range(30):  # 最多等待30秒
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 服务已就绪")
                return True
        except:
            if i % 5 == 0:  # 每5秒打印一次状态
                print(f"  等待中... ({i+1}/30 秒)")
        time.sleep(1)
    return False

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_query(question, top_k=3):
    """测试问答功能"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/query/",
            json={"question": question, "top_k": top_k},
            timeout=120  # 增加超时时间到120秒
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 问题: {question}")
            print(f"   回答: {result.get('answer', '无答案')[:100]}...")
            
            # 安全地访问可能不存在的字段
            processing_time = result.get('processing_time', end_time - start_time)
            source_docs_count = len(result.get('source_documents', []))
            confidence = result.get('confidence', 0.0)
            
            print(f"   处理时间: {processing_time:.2f}秒")
            print(f"   检索文档数: {source_docs_count}")
            print(f"   置信度: {confidence}")
            return True
        else:
            print(f"❌ 问答失败: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ 问答超时: {question}")
        return False
    except Exception as e:
        print(f"❌ 问答异常: {e}")
        return False

def test_with_resume_questions():
    """测试与简历相关的问题"""
    print("\n🧪 测试简历相关问题:")
    
    resume_questions = [
        "What is this person's education background?",
        "他有什么工作经历？", 
        "他掌握了哪些技能？",
        "他有什么项目经验？",
        "他的专业方向是什么？"
    ]
    
    all_passed = True
    for question in resume_questions:
        if not test_query(question):
            all_passed = False
        print("-" * 50)
    
    return all_passed

def main():
    """主测试函数"""
    print("🧪 开始完整系统测试...")
    
    # 0. 等待服务启动
    if not wait_for_service():
        print("💡 请确保服务正在运行: uvicorn app.main:app --reload")
        return False
    
    # 1. 测试健康检查
    if not test_health():
        return False
    
    # 2. 测试简历相关问题
    if not test_with_resume_questions():
        return False
    
    print("🎉 所有测试通过！系统运行正常。")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)