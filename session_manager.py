"""
会话管理模块
Session management module
"""
from typing import Dict, List
import time
import uuid


class ConversationSession:
    """会话类 - 管理单个对话会话"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self.created_at = time.time()
        self.last_updated = time.time()
    
    def add_message(self, role: str, content: str, agent_type: str = None):
        """添加消息到会话历史"""
        message = {
            'role': role,
            'content': content,
            'timestamp': time.time()
        }
        if agent_type:
            message['agent_type'] = agent_type
        
        self.messages.append(message)
        self.last_updated = time.time()
    
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """获取对话上下文（最近N条消息）"""
        # 返回适合LLM的格式（不包含timestamp等额外字段）
        context = []
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        
        for msg in recent_messages:
            context.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return context
    
    def get_all_messages(self) -> List[Dict[str, str]]:
        """获取所有消息"""
        return self.messages.copy()
    
    def clear(self):
        """清空会话历史"""
        self.messages = []
        self.last_updated = time.time()


class SessionManager:
    """会话管理器 - 管理多个用户会话"""
    
    def __init__(self, max_sessions: int = 100, session_timeout: int = 3600):
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout  # 会话超时时间（秒）
    
    def create_session(self) -> str:
        """创建新会话"""
        # 清理过期会话
        self._cleanup_expired_sessions()
        
        # 如果会话数超过限制，删除最旧的会话
        if len(self.sessions) >= self.max_sessions:
            oldest_id = min(self.sessions.keys(), key=lambda k: self.sessions[k].created_at)
            del self.sessions[oldest_id]
        
        session = ConversationSession()
        self.sessions[session.session_id] = session
        return session.session_id
    
    def get_session(self, session_id: str) -> ConversationSession:
        """获取会话，如果不存在则创建"""
        if session_id not in self.sessions:
            session = ConversationSession(session_id)
            self.sessions[session_id] = session
        
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _cleanup_expired_sessions(self):
        """清理过期的会话"""
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session.last_updated > self.session_timeout
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        self._cleanup_expired_sessions()
        return len(self.sessions)
