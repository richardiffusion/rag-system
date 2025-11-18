#!/usr/bin/env python3
"""
专门测试简历问答的脚本
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_resume_questions():
    """测试简历相关问题"""
    questions = [
        {
            "question": "这个人的教育背景是什么？",
            "expected_keywords": ["大学", "学院", "专业", "学历", "学位", "教育"]
        },
        {
            "question": "他有什么工作经历？",
            "expected_keywords": ["公司", "工作", "职位", "经验", "任职"]
        },
        {
            "question": "他掌握了哪些技能？", 
            "expected_keywords": ["技能", "技术", "编程", "语言", "框架"]
        },
        {
            "question": "他有什么项目经验？",
            "expected_keywords": ["项目", "开发", "实现", "设计", "系统"]
        },
        {
            "question": "他的专业方向是什么？",
            "expected_keywords": ["专业", "方向", "领域", "研究", "专注"]
        }
    ]
    
    print("🧪 简历问答测试")
    print("=" * 60)
    
    all_passed = True
    
    for test_case in questions:
        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\n问题: {question}")
        print("期望关键词:", ", ".join(expected_keywords))
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/query/",
                json={"question": question, "top_k": 3},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"回答: {answer[:150]}...")
                
                # 检查是否包含期望的关键词
                found_keywords = [kw for kw in expected_keywords if kw in answer]
                if found_keywords:
                    print(f"✅ 找到关键词: {', '.join(found_keywords)}")
                else:
                    print("⚠️  未找到期望关键词")
                    all_passed = False
                
                # 显示检索到的文档信息
                source_docs = result.get('source_documents', [])
                print(f"📄 检索到 {len(source_docs)} 个相关文档")
                
                for i, doc in enumerate(source_docs[:2]):  # 显示前2个文档
                    content_preview = doc.get('content', '')[:100] + "..." if len(doc.get('content', '')) > 100 else doc.get('content', '')
                    print(f"   文档 {i+1}: {content_preview}")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            all_passed = False
        
        print("-" * 60)
    
    return all_passed

def test_knowledge_boundary():
    """测试知识边界 - 询问简历中没有的信息"""
    print("\n🧪 测试知识边界")
    print("=" * 60)
    
    boundary_questions = [
        "这个人会说法语吗？",
        "他有博士学位吗？",
        "他在谷歌工作过吗？"
    ]
    
    for question in boundary_questions:
        print(f"\n问题: {question}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/query/",
                json={"question": question, "top_k": 2},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"回答: {answer}")
                
                # 检查是否诚实地表示不知道
                if "不知道" in answer or "无法" in answer or "没有" in answer.lower():
                    print("✅ 正确表示知识边界")
                else:
                    print("⚠️  可能超出了知识边界")
                    
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        
        print("-" * 60)
    
    return True

if __name__ == "__main__":
    print("🔍 RAG系统简历问答测试")
    
    # 测试健康状态
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ 服务未运行，请先启动服务")
            sys.exit(1)
    except:
        print("❌ 无法连接到服务，请先启动服务")
        sys.exit(1)
    
    # 运行测试
    success1 = test_resume_questions()
    success2 = test_knowledge_boundary()
    
    if success1 and success2:
        print("\n🎉 所有测试完成！系统运行正常。")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败，请检查系统。")
        sys.exit(1)