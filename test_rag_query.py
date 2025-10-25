#!/usr/bin/env python3
"""
测试RAG查询和生成功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rag.rag_manager import RAGManager
    from llm.llm_manager import LLMManager
    from utils.config import Config
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

def test_rag_query():
    """测试RAG查询功能"""
    print("\n🔍 测试RAG查询功能")

    # 初始化组件
    config = Config()
    llm_manager = LLMManager(config)
    rag_manager = RAGManager()

    # 检查已加载的文档
    docs = rag_manager.list_documents()
    print(f"📚 已加载文档数量: {len(docs)}")
    for doc in docs:
        print(f"  - {doc['filename']} ({doc['format']}) - ID: {doc['id'][:8]}...")

    if not docs:
        print("❌ 没有已加载的文档，请先加载文档")
        return

    # 测试查询
    test_query = "请总结这个文档的内容"
    print(f"\n❓ 测试查询: {test_query}")

    # 步骤1: 只测试检索（不生成回答）
    print("\n📖 步骤1: 测试文档检索")
    query_result = rag_manager.query_documents(test_query, top_k=3)
    print("检索结果:"    print(f"  - 找到的源数量: {query_result.get('total_sources', 0)}")
    print(f"  - 上下文长度: {len(query_result.get('context', ''))} 字符")

    if query_result.get('sources'):
        print("  - 相关文档片段:")
        for i, source in enumerate(query_result['sources'][:2]):  # 只显示前2个
            print(f"    {i+1}. {source['filename']} (相似度: {source['similarity']:.3f})")

    # 显示检索到的上下文内容
    context = query_result.get('context', '')
    if context:
        print("
📄 检索到的上下文内容 (前500字符):"        print(f"  '{context[:500]}{'...' if len(context) > 500 else ''}'")
    else:
        print("❌ 没有检索到上下文内容！")
        return

    # 步骤2: 测试完整RAG生成
    print("
🤖 步骤2: 测试RAG回答生成"    rag_result = rag_manager.generate_rag_response(
        query=test_query,
        top_k=3,
        llm_manager=llm_manager,
        preferred_model='openai'  # 或者 'gemini'
    )

    print("RAG生成结果:"    print(f"  - 响应长度: {len(rag_result.get('response', ''))} 字符")
    print(f"  - 使用文档数量: {rag_result.get('document_count', 0)}")
    print(f"  - 置信度: {rag_result.get('confidence', 0):.3f}")

    response = rag_result.get('response', '')
    if response:
        print("
📝 生成的回答 (前300字符):"        print(f"  '{response[:300]}{'...' if len(response) > 300 else ''}'")

        # 检查回答是否基于文档内容
        context_lower = context.lower()
        response_lower = response.lower()

        # 检查是否包含文档中的关键词（简单检查）
        doc_keywords = ['playbook', 'training', 'llm', 'gpu', 'cluster']  # 基于用户提到的PDF文件名
        found_keywords = [kw for kw in doc_keywords if kw in context_lower and kw in response_lower]

        if found_keywords:
            print(f"✅ 回答似乎基于文档内容 (包含关键词: {found_keywords})")
        else:
            print("⚠️  回答可能不基于文档内容 (未找到相关关键词)")
            print("   建议检查文档内容和检索结果")
    else:
        print("❌ 没有生成回答")

if __name__ == "__main__":
    test_rag_query()
