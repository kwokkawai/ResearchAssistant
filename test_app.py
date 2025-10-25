"""
测试套件
Test suite for Research Assistant
"""
import unittest
import json
from app import app
from session_manager import SessionManager, ConversationSession


class TestSessionManager(unittest.TestCase):
    """会话管理器测试"""
    
    def setUp(self):
        self.manager = SessionManager()
    
    def test_create_session(self):
        """测试创建会话"""
        session_id = self.manager.create_session()
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.manager.sessions)
    
    def test_get_session(self):
        """测试获取会话"""
        session_id = self.manager.create_session()
        session = self.manager.get_session(session_id)
        self.assertIsInstance(session, ConversationSession)
        self.assertEqual(session.session_id, session_id)
    
    def test_add_message(self):
        """测试添加消息"""
        session = ConversationSession()
        session.add_message('user', 'Hello')
        session.add_message('assistant', 'Hi there')
        messages = session.get_all_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[1]['role'], 'assistant')
    
    def test_get_context(self):
        """测试获取上下文"""
        session = ConversationSession()
        for i in range(15):
            session.add_message('user', f'Message {i}')
        context = session.get_context(max_messages=10)
        self.assertEqual(len(context), 10)
    
    def test_clear_session(self):
        """测试清空会话"""
        session = ConversationSession()
        session.add_message('user', 'Test')
        session.clear()
        self.assertEqual(len(session.messages), 0)


class TestFlaskAPI(unittest.TestCase):
    """Flask API测试"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        """测试主页路由"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_status_route(self):
        """测试状态路由"""
        response = self.app.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('provider', data)
        self.assertIn('model', data)
        self.assertIn('active_sessions', data)
    
    def test_agents_route(self):
        """测试智能体列表路由"""
        response = self.app.get('/api/agents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('agents', data)
        self.assertIsInstance(data['agents'], list)
    
    def test_new_session_route(self):
        """测试新建会话路由"""
        response = self.app.post('/api/session/new')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('session_id', data)
    
    def test_session_history_route(self):
        """测试会话历史路由"""
        # 先创建会话
        response = self.app.post('/api/session/new')
        session_id = json.loads(response.data)['session_id']
        
        # 获取历史
        response = self.app.get(f'/api/session/{session_id}/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('messages', data)
    
    def test_clear_session_route(self):
        """测试清空会话路由"""
        # 先创建会话
        response = self.app.post('/api/session/new')
        session_id = json.loads(response.data)['session_id']
        
        # 清空会话
        response = self.app.post(f'/api/session/{session_id}/clear')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
