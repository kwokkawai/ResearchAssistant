#!/usr/bin/env python3
"""
Agent Management Module
Handles dynamic agent definitions, templates, and management operations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class AgentDefinition:
    """Represents a single agent definition"""
    
    def __init__(self, agent_id: str, name: str, description: str, icon: str,
                 color: str, prompt_template: str, enabled: bool = True,
                 template_id: str = None, template_config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color
        self.prompt_template = prompt_template
        self.enabled = enabled
        self.template_id = template_id
        # For backward compatibility, still support direct template_config
        # If template_id is provided, template_config will be resolved later by the manager
        self.template_config = template_config
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def _get_default_template_config(self) -> Dict[str, Any]:
        """Get default template configuration"""
        return {
            "default_model": "openai",
            "preferred_ollama_model": "deepseek-r1:latest",
            "preferred_openai_model": "gpt-4o",
            "preferred_gemini_model": "gemini-1.5-pro",
            "deep_research_enabled": True,
            "web_search_enabled": True,
            "search_engine": "duckduckgo",
            "search_results_count": 10,
            "include_images": False,
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 300,
            # RAG configuration
            "rag_enabled": False,
            "document_links": [],  # List of document paths or directories
            "rag_top_k": 5,
            "rag_context_window": 2
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'prompt_template': self.prompt_template,
            'enabled': self.enabled,
            'template_id': self.template_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentDefinition':
        """Create from dictionary"""
        agent = cls(
            agent_id=data['agent_id'],
            name=data['name'],
            description=data['description'],
            icon=data['icon'],
            color=data['color'],
            prompt_template=data['prompt_template'],
            enabled=data.get('enabled', True),
            template_id=data.get('template_id'),
            template_config=data.get('template_config')
        )
        agent.created_at = data.get('created_at', agent.created_at)
        agent.updated_at = data.get('updated_at', agent.updated_at)
        return agent

class AgentTemplate:
    """Represents an agent template (combination of agents)"""
    
    def __init__(self, template_id: str, name: str, description: str, 
                 agents: List[str], enabled: bool = True):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.agents = agents
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'agents': self.agents,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Include config if it exists
        if hasattr(self, 'config'):
            result['config'] = self.config
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTemplate':
        """Create from dictionary"""
        template = cls(
            template_id=data['template_id'],
            name=data['name'],
            description=data['description'],
            agents=data.get('agents', []),  # 兼容旧格式
            enabled=data.get('enabled', True)
        )
        template.created_at = data.get('created_at', template.created_at)
        template.updated_at = data.get('updated_at', template.updated_at)
        
        # 如果有config字段，设置它
        if 'config' in data:
            template.config = data['config']
        
        return template

class AgentManager:
    """Manages agent definitions and templates"""
    
    def __init__(self, data_file: str = "data/agent_definitions.json"):
        self.data_file = data_file
        self.agents: Dict[str, AgentDefinition] = {}
        self.templates: Dict[str, AgentTemplate] = {}
        self.metadata: Dict[str, Any] = {}
        self.load_data()
    
    def load_data(self):
        """Load agent definitions from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load agents
                self.agents = {}
                for agent_id, agent_data in data.get('agents', {}).items():
                    agent_data['agent_id'] = agent_id
                    self.agents[agent_id] = AgentDefinition.from_dict(agent_data)
                
                # Load templates from separate file
                self._load_templates_from_file()
                
                # Load metadata
                self.metadata = data.get('metadata', {})
            else:
                # Initialize with default data
                self._initialize_default_data()
        except Exception as e:
            print(f"Error loading agent data: {e}")
            self._initialize_default_data()

    def _load_templates_from_file(self):
        """Load templates from agent_definitions.json (templates section)"""
        try:
            # Templates are in the same file as agents (agent_definitions.json)
            agents_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'agent_definitions.json')
            if os.path.exists(agents_file):
                with open(agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    templates_data = data.get('templates', {})
                    self.templates = {}
                    for template_id, template_data in templates_data.items():
                        # Convert template config format to AgentTemplate format
                        agent_template_data = {
                            'template_id': template_id,
                            'name': template_data.get('name', template_id),
                            'description': template_data.get('description', ''),
                            'agents': [],  # Templates don't contain agent lists in new design
                            'enabled': template_data.get('enabled', True),
                            'config': template_data.get('config', {})
                        }
                        template = AgentTemplate.from_dict(agent_template_data)
                        self.templates[template_id] = template
                    print(f"✅ 加载了 {len(self.templates)} 个模板配置")
                    
                    # Log template details for debugging
                    for template_id, template in self.templates.items():
                        if hasattr(template, 'config'):
                            config = template.config
                            print(f"   📋 {template.name}: default_model={config.get('default_model')}, rag_enabled={config.get('rag_enabled')}")
            else:
                print("⚠️  Warning: agent_definitions.json not found")
                self.templates = {}
        except Exception as e:
            print(f"❌ Error loading templates from file: {e}")
            import traceback
            traceback.print_exc()
            self.templates = {}

    def get_agent_template_config(self, agent: AgentDefinition) -> Dict[str, Any]:
        """Get template configuration for an agent, resolving template_id if needed"""
        if agent.template_config:
            # Direct template config (backward compatibility)
            return agent.template_config
        elif agent.template_id and agent.template_id in self.templates:
            # Resolve from template
            template = self.templates[agent.template_id]
            return template.config if hasattr(template, 'config') else {}
        else:
            # Fallback to default
            return self._get_default_template_config()

    def _get_default_template_config(self) -> Dict[str, Any]:
        """Get default template configuration"""
        return {
            "default_model": "openai",
            "preferred_ollama_model": "deepseek-r1:latest",
            "preferred_openai_model": "gpt-4o",
            "preferred_gemini_model": "gemini-1.5-pro",
            "deep_research_enabled": True,
            "web_search_enabled": True,
            "search_engine": "duckduckgo",
            "search_results_count": 10,
            "include_images": False,
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 300,
            "rag_enabled": False,
            "rag_top_k": 5,
            "rag_context_window": 2,
            "document_links": []
        }

    def save_data(self):
        """Save agent definitions to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            data = {
                'agents': {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
                'templates': {template_id: template.to_dict() for template_id, template in self.templates.items()},
                'metadata': {
                    'version': '1.0.0',
                    'last_updated': datetime.now().isoformat(),
                    'total_agents': len(self.agents),
                    'total_templates': len(self.templates)
                }
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving agent data: {e}")
            return False
    
    def _initialize_default_data(self):
        """Initialize with default agent definitions"""
        # This will be populated from the JSON file
        pass
    
    # Agent CRUD operations
    def create_agent(self, name: str, description: str, icon: str, color: str, 
                    prompt_template: str, enabled: bool = True, 
                    template_config: Dict[str, Any] = None) -> str:
        """Create a new agent"""
        agent_id = str(uuid.uuid4())[:8]  # Short ID
        agent = AgentDefinition(agent_id, name, description, icon, color, 
                               prompt_template, enabled, template_config)
        self.agents[agent_id] = agent
        self.save_data()
        return agent_id
    
    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """Update an existing agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        agent.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id not in self.agents:
            return False
        
        # Remove from all templates
        for template in self.templates.values():
            if agent_id in template.agents:
                template.agents.remove(agent_id)
        
        del self.agents[agent_id]
        self.save_data()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[AgentDefinition]:
        """Get all agents"""
        return list(self.agents.values())
    
    def get_enabled_agents(self) -> List[AgentDefinition]:
        """Get only enabled agents"""
        return [agent for agent in self.agents.values() if agent.enabled]
    
    # Template CRUD operations
    def create_template(self, name: str, description: str, agents: List[str], 
                      enabled: bool = True) -> str:
        """Create a new template"""
        template_id = str(uuid.uuid4())[:8]  # Short ID
        template = AgentTemplate(template_id, name, description, agents, enabled)
        self.templates[template_id] = template
        self.save_data()
        return template_id
    
    def update_template(self, template_id: str, **kwargs) -> bool:
        """Update an existing template"""
        if template_id not in self.templates:
            return False

        template = self.templates[template_id]
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now().isoformat()
        self.save_data()
        return True

    def update_template_config(self, template_id: str, config: Dict[str, Any]) -> bool:
        """Update template configuration"""
        if template_id not in self.templates:
            return False

        template = self.templates[template_id]
        template.config = config
        template.updated_at = datetime.now().isoformat()
        
        # Save templates to templates.json
        self.save_templates()
        
        # Also save to agent_definitions.json for backward compatibility
        self.save_data()
        return True
    
    def save_templates(self):
        """Save templates back to agent_definitions.json (templates section)"""
        try:
            agents_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'agent_definitions.json')
            
            # Read the entire file first
            with open(agents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert templates to dictionary format
            templates_data = {}
            for template_id, template in self.templates.items():
                templates_data[template_id] = {
                    'template_id': template.template_id,
                    'name': template.name,
                    'description': template.description,
                    'agents': [],  # Keep empty for new design
                    'config': template.config if hasattr(template, 'config') else {},
                    'enabled': template.enabled if hasattr(template, 'enabled') else True,
                    'created_at': template.created_at,
                    'updated_at': template.updated_at
                }
            
            # Update the templates section
            data['templates'] = templates_data
            
            # Update metadata
            if 'metadata' in data:
                data['metadata']['last_updated'] = datetime.now().isoformat()
                data['metadata']['total_templates'] = len(templates_data)
            
            # Write back to file
            with open(agents_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功保存 {len(templates_data)} 个模板配置到 agent_definitions.json")
            return True
        except Exception as e:
            print(f"❌ Error saving templates to file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_template_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template configuration for mutual exclusivity"""
        web_search = config.get('web_search_enabled', False)
        rag_enabled = config.get('rag_enabled', False)

        # 互斥验证：不能同时启用网络搜索和RAG
        if web_search and rag_enabled:
            # 优先保留RAG，因为它提供更准确的答案
            config['web_search_enabled'] = False
            print("Warning: Both web search and RAG enabled. Disabled web search to maintain consistency.")

        return config
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id not in self.templates:
            return False
        
        del self.templates[template_id]
        self.save_data()
        return True
    
    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> List[AgentTemplate]:
        """Get all templates"""
        return list(self.templates.values())
    
    def get_enabled_templates(self) -> List[AgentTemplate]:
        """Get only enabled templates"""
        return [template for template in self.templates.values() if template.enabled]
    
    # Utility methods
    def get_agent_prompt(self, agent_id: str, query: str, context: Dict[str, Any] = None) -> str:
        """Get formatted prompt for an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return ""
        
        # Build context info
        context_info = ""
        if context and context.get('previous_research'):
            context_info = f"""
            
            之前的研究结果：
            {context['previous_research']}
            
            请基于以上之前的研究结果，回答新的查询。
            """
        
        # Build web search info
        web_search_info = ""
        if context and context.get('web_search_results'):
            web_results = context['web_search_results']
            web_search_info = f"""
            
            网络搜索结果：
            {chr(10).join([f"- {result.get('title', '')}: {result.get('snippet', '')}" for result in web_results[:5]])}
            
            请结合以上网络搜索结果进行分析。
            """
        
        # Build deep research note
        deep_research_note = ""
        if context and context.get('deep_research_enabled'):
            deep_research_note = """

            注意：请进行深度研究分析，提供多角度的见解和综合性的结论。
            """

        # Build RAG note (if RAG is enabled, this should not appear)
        rag_note = ""
        if context and context.get('rag_enabled'):
            rag_note = """

            注意：这是一个基于本地文档的RAG查询，请确保回答完全基于提供的文档内容，不要进行推测或外部知识补充。
            """
        
        # Format the prompt
        return agent.prompt_template.format(
            query=query,
            context_info=context_info,
            web_search_info=web_search_info,
            deep_research_note=deep_research_note,
            rag_note=rag_note
        )
    
    def validate_agent_ids(self, agent_ids: List[str]) -> List[str]:
        """Validate agent IDs and return only valid ones"""
        return [agent_id for agent_id in agent_ids if agent_id in self.agents and self.agents[agent_id].enabled]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the agent system"""
        return {
            'total_agents': len(self.agents),
            'enabled_agents': len(self.get_enabled_agents()),
            'total_templates': len(self.templates),
            'enabled_templates': len(self.get_enabled_templates()),
            'last_updated': self.metadata.get('last_updated', 'Unknown')
        }
    
    
    def update_agent_template_config(self, agent_id: str, config: Dict[str, Any]) -> bool:
        """Update template configuration for a specific agent"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.template_config.update(config)
            agent.updated_at = datetime.now().isoformat()
            self.save_data()
            return True
        return False

# Global agent manager instance
agent_manager = AgentManager()
