"""
Conversation management for continuous research sessions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import uuid

class ConversationTurn:
    """Represents a single turn in the conversation"""
    
    def __init__(self, turn_id: str, query: str, agents: List[str], model: str, 
                 ollama_model: Optional[str] = None, context: Optional[str] = None):
        self.turn_id = turn_id
        self.query = query
        self.agents = agents
        self.model = model
        self.ollama_model = ollama_model
        self.context = context
        self.timestamp = datetime.now().isoformat()
        self.result = None
        self.summary = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'turn_id': self.turn_id,
            'query': self.query,
            'agents': self.agents,
            'model': self.model,
            'ollama_model': self.ollama_model,
            'context': self.context,
            'timestamp': self.timestamp,
            'result': self.result,
            'summary': self.summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary"""
        turn = cls(
            turn_id=data['turn_id'],
            query=data['query'],
            agents=data['agents'],
            model=data['model'],
            ollama_model=data.get('ollama_model'),
            context=data.get('context')
        )
        turn.timestamp = data.get('timestamp', datetime.now().isoformat())
        turn.result = data.get('result')
        turn.summary = data.get('summary')
        return turn

class ConversationSession:
    """Manages a complete conversation session"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.turns: List[ConversationTurn] = []
        self.current_context = ""
        self.metadata: Dict[str, Any] = {}  # Store session-specific data like Shopify credentials
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a new turn to the conversation"""
        self.turns.append(turn)
        # Update context with the latest result
        if turn.summary:
            self.current_context = turn.summary
        elif turn.result and isinstance(turn.result, dict):
            # Extract key information from result
            results_text = "\n\n".join([
                f"Agent: {result.get('agent', 'unknown')}\n"
                f"Response: {result.get('response', result.get('error', 'No response'))}"
                for result in turn.result.get('results', [])
            ])
            self.current_context = results_text
    
    def get_context_for_next_turn(self) -> str:
        """Get context string for the next turn"""
        if not self.turns:
            return ""
        
        context_parts = []
        
        # Add previous turn summaries
        for turn in self.turns[-3:]:  # Last 3 turns for context
            if turn.summary:
                context_parts.append(f"Previous Research ({turn.timestamp}):\n{turn.summary}")
            elif turn.result:
                context_parts.append(f"Previous Research ({turn.timestamp}):\n{turn.query}\n{turn.result}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at,
            'turns': [turn.to_dict() for turn in self.turns],
            'current_context': self.current_context,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create from dictionary"""
        session = cls(session_id=data['session_id'])
        session.created_at = data.get('created_at', datetime.now().isoformat())
        session.turns = [ConversationTurn.from_dict(turn_data) for turn_data in data.get('turns', [])]
        session.current_context = data.get('current_context', "")
        session.metadata = data.get('metadata', {})
        return session

class ConversationManager:
    """Manages multiple conversation sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.current_session_id: Optional[str] = None
    
    def create_new_session(self) -> str:
        """Create a new conversation session"""
        session = ConversationSession()
        self.sessions[session.session_id] = session
        self.current_session_id = session.session_id
        return session.session_id
    
    def get_current_session(self) -> Optional[ConversationSession]:
        """Get the current active session"""
        if self.current_session_id and self.current_session_id in self.sessions:
            return self.sessions[self.current_session_id]
        return None
    
    def add_turn_to_current_session(self, turn: ConversationTurn) -> None:
        """Add a turn to the current session"""
        if not self.current_session_id:
            self.create_new_session()
        
        session = self.sessions[self.current_session_id]
        session.add_turn(turn)
    
    def get_session_context(self) -> str:
        """Get context for the current session"""
        session = self.get_current_session()
        if session:
            return session.get_context_for_next_turn()
        return ""
    
    def export_session(self, session_id: str = None) -> Dict[str, Any]:
        """Export a session for saving"""
        target_session_id = session_id or self.current_session_id
        if target_session_id and target_session_id in self.sessions:
            return self.sessions[target_session_id].to_dict()
        return {}
    
    def import_session(self, session_data: Dict[str, Any]) -> str:
        """Import a session from saved data"""
        session = ConversationSession.from_dict(session_data)
        self.sessions[session.session_id] = session
        self.current_session_id = session.session_id
        return session.session_id
