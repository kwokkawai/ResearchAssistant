"""
LLM Manager for handling different LLM providers
"""

import requests
import json
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from utils.config import Config

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('OLLAMA_BASE_URL')
        self.model = config.get('OLLAMA_MODEL')
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "max_tokens": kwargs.get('max_tokens', 2000)
                }
            }
            
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.get('OPENAI_API_KEY')
        self.model = config.get('OPENAI_MODEL')
        self.temperature = config.get('OPENAI_TEMPERATURE')
        self.max_tokens = config.get('OPENAI_MAX_TOKENS')
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.temperature),
                "max_tokens": kwargs.get('max_tokens', self.max_tokens)
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return bool(self.api_key)

class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.get('GOOGLE_API_KEY')
        self.model = config.get('GEMINI_MODEL')
        self.temperature = config.get('GEMINI_TEMPERATURE')
        self.max_tokens = config.get('GEMINI_MAX_TOKENS')
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Google Gemini API"""
        if not self.api_key:
            raise Exception("Google API key not configured")
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": kwargs.get('temperature', self.temperature),
                    "maxOutputTokens": kwargs.get('max_tokens', self.max_tokens)
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return bool(self.api_key)

class LLMManager:
    """Manager for all LLM providers"""
    
    def __init__(self, config: Config):
        self.config = config
        self.providers = {
            'ollama': OllamaProvider(config),
            'openai': OpenAIProvider(config),
            'gemini': GeminiProvider(config)
        }
    
    def get_provider(self, provider_name: str) -> LLMProvider:
        """Get a specific provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]
    
    def generate_response(self, provider_name: str, prompt: str, **kwargs) -> str:
        """Generate response using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider.is_available():
            raise Exception(f"Provider {provider_name} is not available")
        
        return provider.generate_response(prompt, **kwargs)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        available_models = []
        
        for name, provider in self.providers.items():
            if provider.is_available():
                available_models.append({
                    'name': name,
                    'type': 'local' if name == 'ollama' else 'cloud',
                    'status': 'available'
                })
            else:
                available_models.append({
                    'name': name,
                    'type': 'local' if name == 'ollama' else 'cloud',
                    'status': 'unavailable'
                })
        
        return available_models
