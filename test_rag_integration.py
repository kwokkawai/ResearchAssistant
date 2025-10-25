#!/usr/bin/env python3
"""
测试RAG与智能体集成的完整功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents.agent_manager import AgentManager
    from llm.llm_manager import LLMManager
    from utils.config import Config
    from rag.rag_manager import RAGManager
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

def test_rag_agent_integration():
    """测试RAG与智能体的完整集成"""
    print("\n🔗 测试RAG与智能体集成")

    # 初始化组件
    config = Config()
    llm_manager = LLMManager(config)
    agent_manager = AgentManager(llm_manager)
    rag_manager = RAGManager()

    # 检查已加载的文档
    docs = rag_manager.list_documents()
    print(f"📚 已加载文档数量: {len(docs)}")
    for doc in docs:
        print(f"  - {doc['filename']} ({doc['format']})")

    if not docs:
        print("❌ 没有已加载的文档，请先加载文档")
        return

    # 检查智能体
    agents = agent_manager.agents
    print(f"🤖 可用智能体数量: {len(agents)}")
    for agent_id, agent in agents.items():
        print(f"  - {agent_id}: {agent.name}")

    # 查找技术专家智能体
    tech_expert = None
    for agent_id, agent in agents.items():
        if '技术' in agent.name or 'expert' in agent_id.lower():
            tech_expert = agent_id
            break

    if not tech_expert:
        print("❌ 未找到技术专家智能体")
        return

    print(f"🎯 使用智能体: {tech_expert}")

    # 测试查询
    test_query = "请总结这个文档的内容"
    print(f"\n❓ 测试查询: {test_query}")

    # 执行研究（模拟前端调用）
    print("\n🔬 执行RAG-enabled研究...")
    try:
        results = agent_manager.execute_research(
            query=test_query,
            selected_agents=[tech_expert],
            preferred_model='openai',
            rag_manager=rag_manager
        )

        print("\n📊 研究结果分析:")
        print(f"  - 查询: {results.get('query', '')}")
        print(f"  - RAG配置: {results.get('rag_config', {})}")
        print(f"  - RAG成功: {'✅' if results.get('rag_results') else '❌'}")
        print(f"  - 使用的智能体: {results.get('agents_used', [])}")
        print(f"  - 智能体结果数量: {len(results.get('results', []))}")

        # 检查智能体结果
        agent_results = results.get('results', [])
        for i, result in enumerate(agent_results):
            print(f"\n🤖 智能体 {i+1} 结果:")
            print(f"  - 智能体: {result.get('agent', '')}")
            print(f"  - 基于文档: {result.get('based_on_documents', False)}")
            if result.get('rag_sources'):
                print(f"  - RAG来源数量: {len(result['rag_sources'])}")
            if result.get('error'):
                print(f"  - 错误: {result['error']}")

        # 检查总结
        summary = results.get('summary', '')
        print("\n📝 最终总结:")
        print(f"  长度: {len(summary)} 字符")
        print(f"  内容: {summary[:200]}{'...' if len(summary) > 200 else ''}")

        # 验证总结是否基于文档
        if results.get('rag_results'):
            rag_response = results['rag_results'].get('response', '')
            if summary == rag_response:
                print("✅ 总结正确使用了RAG结果")
            else:
                print("⚠️  总结与RAG结果不一致")
        else:
            print("ℹ️  总结使用了智能体正常回答")

        # 检查是否有RAG错误
        if results.get('rag_error'):
            print(f"❌ RAG错误: {results['rag_error']}")
        else:
            print("✅ 无RAG错误")

        print("\n🎉 测试完成!")

    except Exception as e:
        print(f"❌ 执行研究时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_agent_integration()
