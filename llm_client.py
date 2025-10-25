"""
LLM客户端基类和实现
LLM client base class and implementations
"""
from abc import ABC, abstractmethod
import requests
from typing import List, Dict
from config import Config


class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """生成响应"""
        pass


class OllamaClient(LLMClient):
    """Ollama本地LLM客户端"""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """使用Ollama生成响应"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content', '')
        except Exception as e:
            return f"Ollama错误: {str(e)}"


class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """使用OpenAI API生成响应"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI错误: {str(e)}"


class GeminiClient(LLMClient):
    """Google Gemini API客户端"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model_instance = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("请安装google-generativeai库: pip install google-generativeai")
    
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """使用Google Gemini API生成响应"""
        try:
            # 将消息转换为Gemini格式
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature
                }
            )
            return response.text
        except Exception as e:
            return f"Gemini错误: {str(e)}"
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表转换为单个提示"""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(f"系统指令: {content}")
            elif role == 'user':
                prompt_parts.append(f"用户: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"助手: {content}")
        return "\n\n".join(prompt_parts)


def get_llm_client() -> LLMClient:
    """根据配置获取LLM客户端"""
    provider = Config.LLM_PROVIDER.lower()
    
    if provider == 'ollama':
        return OllamaClient(Config.OLLAMA_BASE_URL, Config.OLLAMA_MODEL)
    elif provider == 'openai':
        if not Config.OPENAI_API_KEY:
            raise ValueError("未设置OPENAI_API_KEY")
        return OpenAIClient(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
    elif provider == 'gemini':
        if not Config.GEMINI_API_KEY:
            raise ValueError("未设置GEMINI_API_KEY")
        return GeminiClient(Config.GEMINI_API_KEY, Config.GEMINI_MODEL)
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
