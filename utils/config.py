"""
Configuration management for the Research Assistant
"""

import os
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file will not be loaded.")

class Config:
    """Configuration class for managing all settings"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables and defaults"""
        return {
            # Flask settings
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
            'DEBUG': os.environ.get('DEBUG', 'True').lower() == 'true',
            'HOST': os.environ.get('HOST', '0.0.0.0'),
            'PORT': int(os.environ.get('PORT', 5050)),
            
            # LLM API Keys
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
            'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', ''),
            'GOOGLE_SEARCH_API_KEY': os.environ.get('GOOGLE_SEARCH_API_KEY', ''),
            'GOOGLE_SEARCH_ENGINE_ID': os.environ.get('GOOGLE_SEARCH_ENGINE_ID', ''),
            
            # Ollama settings
            'OLLAMA_BASE_URL': os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'OLLAMA_MODEL': os.environ.get('OLLAMA_MODEL', 'deepseek-r1:latest'),
            
            # OpenAI settings
            'OPENAI_MODEL': os.environ.get('OPENAI_MODEL', 'gpt-4o'),
            'OPENAI_TEMPERATURE': float(os.environ.get('OPENAI_TEMPERATURE', 0.7)),
            'OPENAI_MAX_TOKENS': int(os.environ.get('OPENAI_MAX_TOKENS', 2000)),
            
            # Google Gemini settings
            'GEMINI_MODEL': os.environ.get('GEMINI_MODEL', 'gemini-1.5-pro'),
            'GEMINI_TEMPERATURE': float(os.environ.get('GEMINI_TEMPERATURE', 0.7)),
            'GEMINI_MAX_TOKENS': int(os.environ.get('GEMINI_MAX_TOKENS', 2000)),
            
            # Agent settings
            'MAX_AGENTS_PER_QUERY': int(os.environ.get('MAX_AGENTS_PER_QUERY', 5)),
            'AGENT_TIMEOUT': int(os.environ.get('AGENT_TIMEOUT', 300)),
            
            # Research settings
            'MAX_RESEARCH_DEPTH': int(os.environ.get('MAX_RESEARCH_DEPTH', 3)),
            'ENABLE_WEB_SEARCH': os.environ.get('ENABLE_WEB_SEARCH', 'True').lower() == 'true',
            
            # Shopify API settings
            # Note: SHOPIFY_SHOP_DOMAIN is deprecated, use SHOPIFY_SHOP_URL
            'SHOPIFY_SHOP_URL': os.environ.get('SHOPIFY_SHOP_URL', '') or os.environ.get('SHOPIFY_SHOP_DOMAIN', ''),
            'SHOPIFY_ACCESS_TOKEN': os.environ.get('SHOPIFY_ACCESS_TOKEN', ''),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        self.config.update(updates)
