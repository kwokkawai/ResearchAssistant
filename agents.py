"""
多智能体系统
Multi-agent system with specialized agents
"""
from typing import List, Dict
from llm_client import LLMClient


class Agent:
    """智能体基类"""
    
    def __init__(self, name: str, role: str, llm_client: LLMClient):
        self.name = name
        self.role = role
        self.llm_client = llm_client
    
    def process(self, query: str, context: List[Dict[str, str]] = None) -> str:
        """处理查询"""
        messages = []
        
        # 添加系统提示
        messages.append({
            "role": "system",
            "content": self.role
        })
        
        # 添加上下文
        if context:
            messages.extend(context)
        
        # 添加当前查询
        messages.append({
            "role": "user",
            "content": query
        })
        
        # 生成响应
        return self.llm_client.generate(messages)


class ResearchAgent(Agent):
    """研究智能体 - 专注于学术研究和文献分析"""
    
    def __init__(self, llm_client: LLMClient):
        role = """你是一个专业的研究助手，擅长学术研究、文献分析和科研方法论。
你的职责包括：
1. 分析和总结学术文献
2. 提供研究方法建议
3. 帮助构建研究框架
4. 解释复杂的学术概念
5. 提供引用和参考建议

请始终保持专业和准确，提供有依据的信息。"""
        super().__init__("研究助手", role, llm_client)


class DataAnalysisAgent(Agent):
    """数据分析智能体 - 专注于数据处理和统计分析"""
    
    def __init__(self, llm_client: LLMClient):
        role = """你是一个专业的数据分析专家，擅长统计分析、数据可视化和数据解释。
你的职责包括：
1. 提供数据分析方法建议
2. 解释统计概念和方法
3. 帮助设计数据收集策略
4. 建议合适的可视化方法
5. 解读数据分析结果

请提供清晰、准确的数据分析指导。"""
        super().__init__("数据分析专家", role, llm_client)


class WritingAgent(Agent):
    """写作智能体 - 专注于学术写作和论文撰写"""
    
    def __init__(self, llm_client: LLMClient):
        role = """你是一个专业的学术写作顾问，擅长论文写作、学术表达和文档编辑。
你的职责包括：
1. 提供写作建议和技巧
2. 改进学术表达和语言
3. 帮助组织论文结构
4. 提供引用格式建议
5. 审阅和改进文本质量

请提供专业、建设性的写作指导。"""
        super().__init__("写作顾问", role, llm_client)


class GeneralAgent(Agent):
    """通用智能体 - 处理一般性问题和综合任务"""
    
    def __init__(self, llm_client: LLMClient):
        role = """你是一个全能的研究助手，能够处理各种类型的研究相关问题。
你的职责包括：
1. 回答一般性研究问题
2. 提供综合性建议
3. 协调不同研究任务
4. 提供创意和头脑风暴
5. 解答疑惑和提供指导

请保持友好、专业，并根据用户需求灵活调整响应。"""
        super().__init__("通用助手", role, llm_client)


class AgentCoordinator:
    """智能体协调器 - 管理和调度多个智能体"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.agents = {
            'research': ResearchAgent(llm_client),
            'data': DataAnalysisAgent(llm_client),
            'writing': WritingAgent(llm_client),
            'general': GeneralAgent(llm_client)
        }
    
    def route_query(self, query: str) -> str:
        """路由查询到合适的智能体"""
        # 简单的关键词路由策略
        query_lower = query.lower()
        
        # 研究相关关键词
        research_keywords = ['研究', '文献', '论文', '学术', '理论', '方法论', 'research', 'literature', 'academic']
        # 数据分析关键词
        data_keywords = ['数据', '统计', '分析', '可视化', '图表', 'data', 'analysis', 'statistical']
        # 写作关键词
        writing_keywords = ['写作', '撰写', '编辑', '表达', '语言', 'writing', 'editing', 'expression']
        
        if any(keyword in query_lower for keyword in research_keywords):
            return 'research'
        elif any(keyword in query_lower for keyword in data_keywords):
            return 'data'
        elif any(keyword in query_lower for keyword in writing_keywords):
            return 'writing'
        else:
            return 'general'
    
    def process(self, query: str, agent_type: str = None, context: List[Dict[str, str]] = None) -> Dict[str, str]:
        """处理查询并返回结果"""
        # 如果未指定智能体类型，自动路由
        if agent_type is None:
            agent_type = self.route_query(query)
        
        # 确保智能体类型有效
        if agent_type not in self.agents:
            agent_type = 'general'
        
        agent = self.agents[agent_type]
        response = agent.process(query, context)
        
        return {
            'agent': agent.name,
            'agent_type': agent_type,
            'response': response
        }
    
    def get_agent_list(self) -> List[Dict[str, str]]:
        """获取所有可用智能体的列表"""
        return [
            {'type': 'research', 'name': '研究助手', 'description': '学术研究和文献分析'},
            {'type': 'data', 'name': '数据分析专家', 'description': '数据处理和统计分析'},
            {'type': 'writing', 'name': '写作顾问', 'description': '学术写作和论文撰写'},
            {'type': 'general', 'name': '通用助手', 'description': '处理一般性问题'}
        ]
