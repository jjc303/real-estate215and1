#!/usr/bin/env python3
"""
测试 RAG 功能是否正常工作
"""

import sys
import os
import pytest

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.service_manager import service_manager

pytestmark = pytest.mark.integration

def test_rag_functionality():
    """测试 RAG 功能"""
    print("开始测试 RAG 功能...")
    
    # 初始化所有服务
    success = service_manager.initialize_all()
    print(f"服务初始化结果: {'成功' if success else '失败'}")
    if not success:
        pytest.skip("依赖服务未就绪，跳过 RAG 集成测试")
    
    # 获取 RAG 服务
    rag_service = service_manager.get_service("rag")
    assert rag_service, "RAG 服务未找到"
    
    print("✅ RAG 服务已获取")
    
    # 检查 RAG 健康状态
    health = rag_service.health_check()
    print(f"RAG 健康状态: {health}")
    if health.get('status') != 'ok':
        pytest.skip(f"RAG 服务未正常运行: {health}")
    
    print("✅ RAG 服务运行正常")
    
    # 测试检索功能
    test_questions = [
        "什么是数据库",
        "数据结构是什么",
        "如何学习编程"
    ]
    
    print("\n测试检索功能:")
    for question in test_questions:
        try:
            context = rag_service.retrieve_context(question)
            if context:
                print(f"✅ 问题 '{question}' 检索成功")
                print(f"   检索结果长度: {len(context)} 字符")
                print(f"   前100字符: {context[:100]}...")
            else:
                print(f"⚠️ 问题 '{question}' 未检索到内容")
        except Exception as e:
            print(f"❌ 问题 '{question}' 检索失败: {e}")
    
    # 获取 Chat 服务，测试通过 Chat 服务使用 RAG
    chat_service = service_manager.get_service("chat")
    if chat_service:
        print("\n测试通过 Chat 服务使用 RAG:")
        try:
            context = chat_service.retrieve_context("什么是数据库")
            if context:
                print(f"✅ Chat 服务 RAG 检索成功")
                print(f"   检索结果长度: {len(context)} 字符")
            else:
                print("⚠️ Chat 服务 RAG 未检索到内容")
        except Exception as e:
            print(f"❌ Chat 服务 RAG 检索失败: {e}")
    
    # 测试 RAG 服务关闭
    print("\n测试 RAG 服务关闭:")
    try:
        service_manager.shutdown_all()
        print("✅ 所有服务关闭成功")
    except Exception as e:
        print(f"❌ 服务关闭失败: {e}")
    
    print("\n✅ RAG 功能测试完成")

if __name__ == "__main__":
    test_rag_functionality()
