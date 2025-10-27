"""
Base Agent class and Agent Manager for the Research Assistant
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import threading
import os
import re
from datetime import datetime
from llm.llm_manager import LLMManager
from management.agent_manager import agent_manager as dynamic_agent_manager
from utils.config import Config

class Agent(ABC):
    """Abstract base class for all research agents"""
    
    def __init__(self, name: str, description: str, llm_manager: LLMManager):
        self.name = name
        self.description = description
        self.llm_manager = llm_manager
        self.preferred_provider = 'openai'  # Default provider
    
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a research query and return results"""
        pass
    
    @abstractmethod
    def get_specialization(self) -> str:
        """Return the specialization area of this agent"""
        pass
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using the preferred LLM provider"""
        try:
            return self.llm_manager.generate_response(
                self.preferred_provider, 
                prompt, 
                **kwargs
            )
        except Exception as e:
            # Fallback to other providers
            for provider in ['ollama', 'gemini']:
                if provider != self.preferred_provider:
                    try:
                        return self.llm_manager.generate_response(provider, prompt, **kwargs)
                    except:
                        continue
            raise Exception(f"All LLM providers failed: {str(e)}")
    
    def set_preferred_provider(self, provider: str):
        """Set the preferred LLM provider"""
        self.preferred_provider = provider

class ResearchAgent(Agent):
    """General research agent for broad queries"""
    
    def __init__(self, llm_manager: LLMManager):
        super().__init__(
            name="research_agent",
            description="General research agent for broad queries and analysis",
            llm_manager=llm_manager
        )
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process general research queries"""
        # Build context-aware prompt
        context_info = ""
        web_search_info = ""
        
        if context and context.get('previous_research'):
            context_info = f"""
            
            之前的研究结果：
            {context['previous_research']}
            
            请基于以上之前的研究结果，回答新的查询。
            """
        
        if context and context.get('web_search_results'):
            web_results = context['web_search_results']
            web_search_info = f"""
            
            网络搜索结果：
            {chr(10).join([f"- {result.get('title', '')}: {result.get('snippet', '')}" for result in web_results[:5]])}
            
            请结合以上网络搜索结果进行分析。
            """
        
        deep_research_note = ""
        if context and context.get('deep_research_enabled'):
            deep_research_note = """
            
            注意：请进行深度研究分析，提供多角度的见解和综合性的结论。
            """
        
        prompt = f"""
        作为一个研究助手，请分析以下查询并提供全面的研究结果：
        
        查询: {query}{context_info}{web_search_info}{deep_research_note}
        
        请提供：
        1. 查询的核心主题分析
        2. 相关的主要概念和术语
        3. 可能的研究方向
        4. 建议的进一步研究问题
        
        请用中文回答，结构清晰，内容详实。
        """
        
        try:
            response = self.generate_response(prompt)
            return {
                'agent': self.name,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
        except Exception as e:
            return {
                'agent': self.name,
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
    
    def get_specialization(self) -> str:
        return "general_research"

class TechnicalAgent(Agent):
    """Technical analysis agent for technical queries"""
    
    def __init__(self, llm_manager: LLMManager):
        super().__init__(
            name="technical_agent",
            description="Technical analysis agent for programming, engineering, and technical queries",
            llm_manager=llm_manager
        )
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process technical queries"""
        # Build context-aware prompt
        context_info = ""
        if context and context.get('previous_research'):
            context_info = f"""
            
            之前的研究结果：
            {context['previous_research']}
            
            请基于以上之前的研究结果，回答新的技术查询。
            """
        
        prompt = f"""
        作为一个技术分析专家，请分析以下技术查询：
        
        查询: {query}{context_info}
        
        请提供：
        1. 技术概念解释
        2. 实现方案或解决方案
        3. 最佳实践建议
        4. 相关技术栈和工具
        5. 潜在的技术挑战和解决方案
        
        请用中文回答，提供具体的技术细节和代码示例（如适用）。
        """
        
        try:
            response = self.generate_response(prompt)
            return {
                'agent': self.name,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
        except Exception as e:
            return {
                'agent': self.name,
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
    
    def get_specialization(self) -> str:
        return "technical_analysis"

class AcademicAgent(Agent):
    """Academic research agent for scholarly queries"""
    
    def __init__(self, llm_manager: LLMManager):
        super().__init__(
            name="academic_agent",
            description="Academic research agent for scholarly and academic queries",
            llm_manager=llm_manager
        )
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process academic queries"""
        prompt = f"""
        作为一个学术研究专家，请分析以下学术查询：
        
        查询: {query}
        
        请提供：
        1. 学术背景和理论基础
        2. 相关研究领域和文献
        3. 研究方法建议
        4. 学术写作建议
        5. 进一步研究方向
        
        请用中文回答，注重学术严谨性和理论深度。
        """
        
        try:
            response = self.generate_response(prompt)
            return {
                'agent': self.name,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
        except Exception as e:
            return {
                'agent': self.name,
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
    
    def get_specialization(self) -> str:
        return "academic_research"

class BusinessAgent(Agent):
    """Business analysis agent for business and market queries"""
    
    def __init__(self, llm_manager: LLMManager):
        super().__init__(
            name="business_agent",
            description="Business analysis agent for business strategy and market analysis",
            llm_manager=llm_manager
        )
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process business queries"""
        prompt = f"""
        作为一个商业分析专家，请分析以下商业查询：
        
        查询: {query}
        
        请提供：
        1. 市场分析和趋势
        2. 商业机会评估
        3. 竞争分析
        4. 战略建议
        5. 风险评估和缓解措施
        
        请用中文回答，注重商业实用性和可操作性。
        """
        
        try:
            response = self.generate_response(prompt)
            return {
                'agent': self.name,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
        except Exception as e:
            return {
                'agent': self.name,
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'specialization': self.get_specialization()
            }
    
    def get_specialization(self) -> str:
        return "business_analysis"

class DynamicAgent(Agent):
    """Dynamic agent that uses definitions from the management system"""
    
    def __init__(self, name: str, description: str, llm_manager: LLMManager, agent_definition):
        super().__init__(name, description, llm_manager)
        self.agent_definition = agent_definition

    @property
    def template_config(self):
        """Get template config from agent definition, resolving template_id if needed"""
        return dynamic_agent_manager.get_agent_template_config(self.agent_definition)
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query using dynamic prompt template"""
        try:
            # Check if RAG is enabled - if so, use RAG results directly
            if context and context.get('rag_enabled') and context.get('rag_results'):
                rag_results = context['rag_results']
                # For RAG-enabled agents, return the RAG response directly
                return {
                    'agent': self.name,
                    'query': query,
                    'response': rag_results.get('response', 'RAG回答不可用'),
                    'timestamp': datetime.now().isoformat(),
                    'agent_id': self.agent_definition.agent_id,
                    'rag_sources': rag_results.get('sources', []),
                    'based_on_documents': True
                }

            # Get formatted prompt from dynamic agent manager
            prompt = dynamic_agent_manager.get_agent_prompt(
                self.agent_definition.agent_id,
                query,
                context
            )

            response = self.generate_response(prompt)
            return {
                'agent': self.name,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'agent_id': self.agent_definition.agent_id
            }
        except Exception as e:
            return {
                'agent': self.name,
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent_id': self.agent_definition.agent_id
            }
    
    def get_specialization(self) -> str:
        """Get agent specialization"""
        return self.agent_definition.description

class AgentManager:
    """Manager for all research agents"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents from dynamic definitions"""
        try:
            # Get enabled agents from dynamic manager
            dynamic_agents = dynamic_agent_manager.get_enabled_agents()
            
            for agent_def in dynamic_agents:
                # 🔧 Special handling for Shopify agent - use dedicated ShopifyInteractiveAgent
                if agent_def.agent_id == 'shopify':
                    print(f"🛍️ 正在加载 Shopify Interactive Agent...")
                    from agents.shopify_agent import ShopifyInteractiveAgent
                    agent = ShopifyInteractiveAgent(
                        name=agent_def.name,
                        description=agent_def.description,
                        llm_manager=self.llm_manager
                    )
                    # Store agent definition for template config access
                    agent.agent_definition = agent_def
                    self.agents[agent_def.agent_id] = agent
                    print(f"✅ Shopify Interactive Agent 已加载")
                else:
                    # Create dynamic agent instance for other agents
                    agent = DynamicAgent(
                        name=agent_def.name,
                        description=agent_def.description,
                        llm_manager=self.llm_manager,
                        agent_definition=agent_def
                    )
                    self.agents[agent_def.agent_id] = agent
                
        except Exception as e:
            print(f"Error initializing dynamic agents: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to default agents
            self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default agents as fallback"""
        # Create default agents if dynamic loading fails
        self.agents = {
            'research': ResearchAgent(
                name="研究助手",
                description="通用研究分析智能体",
                llm_manager=self.llm_manager
            ),
            'technical': TechnicalAgent(
                name="技术专家",
                description="技术问题分析智能体",
                llm_manager=self.llm_manager
            ),
            'academic': AcademicAgent(
                name="学术专家",
                description="学术研究智能体",
                llm_manager=self.llm_manager
            ),
            'business': BusinessAgent(
                name="商业分析师",
                description="商业分析智能体",
                llm_manager=self.llm_manager
            )
        }
    
    def get_agent(self, agent_name: str) -> Agent:
        """Get a specific agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        return self.agents[agent_name]
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents"""
        return [
            {
                'name': name,
                'description': agent.description,
                'specialization': agent.get_specialization()
            }
            for name, agent in self.agents.items()
        ]

    def _get_default_deep_research_options(self, selected_agents: List[str]) -> Dict[str, Any]:
        """Get default deep research options from agent template configs"""
        default_options = {
            'enableDeepResearch': False,
            'enableWebSearch': False,
            'searchEngine': 'duckduckgo',
            'searchResults': 10,
            'includeImages': False
        }

        if not selected_agents:
            return default_options

        # Shopify助手强制禁用网络搜索和深度研究
        if 'shopify' in selected_agents:
            default_options['enableDeepResearch'] = False
            default_options['enableWebSearch'] = False
            default_options['searchResults'] = 0
            return default_options

        # Get template config from the first selected agent
        # (If multiple agents are selected, use the first one's config as default)
        first_agent_id = selected_agents[0]
        agent = self.agents.get(first_agent_id)

        if agent and hasattr(agent, 'template_config') and agent.template_config:
            template_config = agent.template_config

            # Map template config to deep research options
            default_options.update({
                'enableDeepResearch': template_config.get('deep_research_enabled', False),
                'enableWebSearch': template_config.get('web_search_enabled', False),
                'searchEngine': template_config.get('search_engine', 'duckduckgo'),
                'searchResults': template_config.get('search_results_count', 10),
                'includeImages': template_config.get('include_images', False)
            })

        return default_options

    def execute_research(self, query: str, selected_agents: List[str] = None, preferred_model: str = 'openai', context: str = '', deep_research_options: Dict[str, Any] = None, rag_manager=None, session_id: str = None) -> Dict[str, Any]:
        """Execute research using selected agents"""
        if selected_agents is None:
            selected_agents = list(self.agents.keys())

        # 强制禁用Shopify助手的网络搜索和RAG功能
        if 'shopify' in selected_agents:
            print("🛡️ 检测到Shopify助手，强制禁用网络搜索和RAG功能（仅使用Shopify API）")
            if deep_research_options is None:
                deep_research_options = {}
            deep_research_options['enableWebSearch'] = False
            deep_research_options['enableDeepResearch'] = False
            rag_manager = None  # 禁用RAG管理器

        # Get default settings from agent template configs
        default_deep_research_options = self._get_default_deep_research_options(selected_agents)

        # Merge user settings with defaults
        # Only override defaults with user settings that are explicitly provided (not None/empty)
        if deep_research_options:
            merged_options = default_deep_research_options.copy()
            # Only update with non-None, non-empty values from user
            for key, value in deep_research_options.items():
                # Only override if the value is meaningful (not None, not empty string)
                if value is not None and value != '':
                    merged_options[key] = value
        else:
            merged_options = default_deep_research_options
        
        print(f"🔧 深度研究选项合并结果:")
        print(f"   默认选项: {default_deep_research_options}")
        print(f"   用户选项: {deep_research_options}")
        print(f"   合并后: {merged_options}")

        # Check for RAG configuration and model settings from the first agent's template
        rag_config = None
        template_model = None
        template_specific_model = None
        
        if selected_agents and len(selected_agents) > 0:
            first_agent = self.agents.get(selected_agents[0])
            if first_agent and hasattr(first_agent, 'template_config') and first_agent.template_config:
                template_config = first_agent.template_config
                
                # Get model configuration from template
                template_model = template_config.get('default_model', None)
                if template_model == 'openai':
                    template_specific_model = template_config.get('preferred_openai_model', 'gpt-4o')
                elif template_model == 'gemini':
                    template_specific_model = template_config.get('preferred_gemini_model', 'gemini-1.5-pro')
                elif template_model == 'ollama':
                    template_specific_model = template_config.get('preferred_ollama_model', None)
                
                # Log template model configuration
                print(f"🔧 智能体模板配置:")
                print(f"   模板模型类型: {template_model}")
                print(f"   模板具体模型: {template_specific_model}")
                print(f"   RAG启用: {template_config.get('rag_enabled', False)}")
                print(f"   网络搜索启用: {template_config.get('web_search_enabled', False)}")
                if template_config.get('web_search_enabled', False):
                    search_engine = template_config.get('search_engine', 'duckduckgo')
                    search_results = template_config.get('search_results_count', 10)
                    print(f"   🔍 搜索引擎: {search_engine}")
                    print(f"   📊 搜索结果数: {search_results}")
                
                # Check RAG configuration
                if template_config.get('rag_enabled', False) and template_config.get('document_links'):
                    rag_config = {
                        'enabled': True,
                        'document_links': template_config.get('document_links', []),
                        'top_k': template_config.get('rag_top_k', 5),
                        'context_window': template_config.get('rag_context_window', 2)
                    }
                    print(f"   📄 文档链接: {rag_config['document_links']}")
                    print(f"   📊 Top-K: {rag_config['top_k']}")
        
        # Use template model if available, otherwise fall back to user-provided preferred_model
        if template_model:
            actual_model = template_model
            actual_specific_model = template_specific_model
            print(f"✅ 使用模板配置的模型: {actual_model} ({actual_specific_model})")
        else:
            actual_model = preferred_model
            actual_specific_model = None
            print(f"⚠️  未找到模板模型配置，使用默认: {actual_model}")
        
        # Update LLM manager with the specific model
        if actual_specific_model:
            try:
                if actual_model == 'ollama':
                    self.llm_manager.providers['ollama'].model = actual_specific_model
                    print(f"🔄 设置Ollama模型: {actual_specific_model}")
                elif actual_model == 'openai':
                    self.llm_manager.providers['openai'].model = actual_specific_model
                    print(f"🔄 设置OpenAI模型: {actual_specific_model}")
                elif actual_model == 'gemini':
                    self.llm_manager.providers['gemini'].model = actual_specific_model
                    print(f"🔄 设置Gemini模型: {actual_specific_model}")
            except Exception as e:
                print(f"⚠️  设置模型失败: {e}")

        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'agents_used': selected_agents,
            'preferred_model': actual_model,  # Use template model, not user-provided model
            'deep_research_options': merged_options,
            'rag_config': rag_config,
            'web_search_results': [],
            'rag_results': None,
            'results': []
        }

        # Use merged options for web search
        deep_research_options = merged_options

        # Perform RAG search if enabled (takes precedence over web search)
        rag_success = False
        if rag_config and rag_config.get('enabled') and rag_manager:
            try:
                print("Performing RAG search instead of web search")
                rag_result = rag_manager.generate_rag_response(
                    query=query,
                    top_k=rag_config.get('top_k', 5),
                    llm_manager=self.llm_manager,
                    preferred_model=actual_model  # Use template model for RAG
                )

                # Check if RAG result is valid (not an error message)
                rag_response = rag_result.get('response', '')
                if rag_response and not rag_response.startswith('基于文档内容的回答生成失败') and not 'error' in rag_response.lower():
                    results['rag_results'] = rag_result
                    rag_success = True
                    # Skip web search when RAG is enabled and successful
                    deep_research_options['enableWebSearch'] = False
                    print("RAG search successful")
                else:
                    print(f"RAG search returned invalid result: {rag_response[:100]}...")
                    results['rag_error'] = f"RAG返回无效结果: {rag_response[:100]}"
                    # Disable RAG for this query since it failed
                    rag_config['enabled'] = False
            except Exception as e:
                print(f"RAG search failed: {e}")
                results['rag_error'] = str(e)
                # Disable RAG for this query since it failed
                if rag_config:
                    rag_config['enabled'] = False

        # Perform web search if enabled (and RAG is not enabled)
        if deep_research_options and deep_research_options.get('enableWebSearch'):
            try:
                from search.web_search import web_search_manager

                # Set search provider
                search_engine = deep_research_options.get('searchEngine', 'duckduckgo')
                config = Config()
                
                print(f"🔍 执行网络搜索:")
                print(f"   搜索引擎: {search_engine}")

                if search_engine == 'google':
                    # Get Google Search API credentials from config
                    google_api_key = config.get('GOOGLE_SEARCH_API_KEY', '')
                    google_engine_id = config.get('GOOGLE_SEARCH_ENGINE_ID', '')

                    if google_api_key and google_engine_id:
                        try:
                            web_search_manager.set_provider('google',
                                api_key=google_api_key,
                                search_engine_id=google_engine_id
                            )
                            print("   ✅ 使用 Google Custom Search API")
                        except Exception as e:
                            print(f"   ❌ Google Search API 初始化失败: {e}")
                            print("   ⚠️  回退到 DuckDuckGo")
                            web_search_manager.set_provider('duckduckgo')
                            search_engine = 'duckduckgo'
                    else:
                        print("   ⚠️  Google Search API 凭据未配置，回退到 DuckDuckGo")
                        web_search_manager.set_provider('duckduckgo')
                        search_engine = 'duckduckgo'
                else:
                    web_search_manager.set_provider(search_engine)
                    print(f"   ✅ 使用 {search_engine} 搜索引擎")

                # Perform search
                num_results = deep_research_options.get('searchResults', 10)
                print(f"   📊 搜索结果数: {num_results}")
                search_results = web_search_manager.search_with_context(query, context, num_results)
                results['web_search_results'] = search_results
                print(f"   ✅ 网络搜索完成，获得 {len(search_results)} 个结果")

            except Exception as e:
                print(f"Web search error: {e}")
                results['web_search_error'] = str(e)
        
        # Execute agents in parallel using threading
        threads = []
        agent_results = {}
        
        def run_agent(agent_name):
            try:
                agent = self.get_agent(agent_name)
                # Pass context, web search results, and RAG results to the agent
                context_dict = {'previous_research': context} if context else {}
                
                # 🔑 Add session_id to context for Shopify agent
                if session_id:
                    context_dict['session_id'] = session_id
                
                if deep_research_options and deep_research_options.get('enableWebSearch'):
                    context_dict['web_search_results'] = results.get('web_search_results', [])
                    context_dict['deep_research_enabled'] = deep_research_options.get('enableDeepResearch', False)

                # Add RAG results only if RAG was successful
                if rag_success and results.get('rag_results'):
                    context_dict['rag_results'] = results['rag_results']
                    context_dict['rag_enabled'] = True
                
                # 🛍️ For Shopify agent, add flag to include raw data in response
                if agent_name == 'shopify':
                    context_dict['include_raw_data'] = True
                
                result = agent.process_query(query, context_dict)
                agent_results[agent_name] = result
            except Exception as e:
                agent_results[agent_name] = {
                    'agent': agent_name,
                    'query': query,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Start threads for each agent
        for agent_name in selected_agents:
            if agent_name in self.agents:
                thread = threading.Thread(target=run_agent, args=(agent_name,))
                threads.append(thread)
                thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=300)  # 300 second timeout
        
        # Collect results
        results['results'] = list(agent_results.values())

        # Generate summary using the template model
        # If RAG was successful, use RAG results for summary generation
        if rag_success and results.get('rag_results'):
            results['summary'] = results['rag_results'].get('response', 'RAG回答生成失败')
            results['rag_sources'] = results['rag_results'].get('sources', [])
            print("Using RAG results for final summary")
        else:
            # 🔧 所有查询都必须通过LLM生成总结
            print("📝 为所有查询生成LLM总结")
            results['summary'] = self._generate_summary(query, agent_results, actual_model, results.get('web_search_results', []))

            if results.get('rag_error'):
                print(f"RAG was enabled but failed, using normal agent responses for summary. RAG error: {results['rag_error']}")

        return results
    
    def _generate_summary(self, query: str, agent_results: Dict[str, Any], preferred_model: str = 'openai', web_search_results: List[Dict[str, Any]] = None) -> str:
        """Generate a summary of all agent results using the preferred model"""
        try:
            # Create a summary prompt
            results_text_parts = []
            for result in agent_results.values():
                agent = result.get('agent', 'unknown')
                response = result.get('response', result.get('error', 'No response'))
                
                # 🔧 添加API数据作为上下文（对于Shopify等有api_data的代理）
                api_data = result.get('api_data')
                if api_data:
                    import json
                    api_data_str = json.dumps(api_data, indent=2, ensure_ascii=False)
                    results_text_parts.append(
                        f"Agent: {agent}\n"
                        f"Response: {response}\n"
                        f"API Data: {api_data_str}"
                    )
                else:
                    results_text_parts.append(
                        f"Agent: {agent}\n"
                        f"Response: {response}"
                    )
            
            results_text = "\n\n".join(results_text_parts)
            
            # Add web search results to summary if available
            web_search_info = ""
            if web_search_results and len(web_search_results) > 0:
                web_search_info = f"""
            
            网络搜索结果:
            {chr(10).join([f"- {result.get('title', '')}: {result.get('snippet', '')}" for result in web_search_results[:5]])}
            """
            
            summary_prompt = f"""
            请基于以下多个智能体的研究结果和网络搜索结果，生成一个简洁的研究总结：

            原始查询: {query}

            各智能体结果:
            {results_text}{web_search_info}

            请提供一个简洁明了的总结，要求：
            1. 直接回答用户的问题，不要使用表格格式
            2. 整合所有智能体的发现和网络搜索信息
            3. 提供准确、权威的答案
            4. 如果涉及事实性问题，直接给出答案
            5. 保持简洁，避免冗长的分析
            6. 基于API数据生成人类可读的总结，不要直接输出JSON或API数据
            7. 提取API数据中的关键信息，用自然语言描述

            请用中文回答，内容要简洁明了，确保包含网络搜索的最新信息。
            """
            
            # Try to use the preferred model, fallback to others if it fails
            try:
                return self.llm_manager.generate_response(preferred_model, summary_prompt)
            except Exception as e:
                print(f"Preferred model {preferred_model} failed: {e}")
                # Try other available models
                for fallback_model in ['ollama', 'gemini', 'openai']:
                    if fallback_model != preferred_model:
                        try:
                            return self.llm_manager.generate_response(fallback_model, summary_prompt)
                        except:
                            continue
                raise Exception(f"All models failed to generate summary")
            
        except Exception as e:
            return f"无法生成总结: {str(e)}"
