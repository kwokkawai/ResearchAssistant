#!/usr/bin/env python3
"""
测试RAG强制重新加载功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rag.rag_manager import RAGManager
    print("✅ RAG模块导入成功")
except ImportError as e:
    print(f"❌ RAG模块导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

def test_force_reload():
    """测试强制重新加载功能"""
    print("\n🔄 测试强制重新加载功能")

    # 创建RAG管理器
    rag_manager = RAGManager()

    # 测试路径
    test_path = "/Users/pkwok/DocBase/AI/"

    print(f"测试路径: {test_path}")

    # 第一次加载（正常）
    print("\n📚 第一次加载...")
    result1 = rag_manager.add_documents_from_directory(test_path, force_reload=False)
    print(f"结果: {result1}")

    # 第二次加载（应该跳过）
    print("\n📚 第二次加载（不强制）...")
    result2 = rag_manager.add_documents_from_directory(test_path, force_reload=False)
    print(f"结果: {result2}")

    # 第三次加载（强制重新加载）
    print("\n🔄 第三次加载（强制重新加载）...")
    result3 = rag_manager.add_documents_from_directory(test_path, force_reload=True)
    print(f"结果: {result3}")

    # 检查当前文档
    print("\n📋 当前加载的文档:")
    docs = rag_manager.list_documents()
    for doc in docs:
        print(f"  - {doc['filename']} ({doc['format']})")

    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_force_reload()
