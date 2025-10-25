"""
Flask应用主文件
Flask application main file
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from config import Config
from llm_client import get_llm_client
from agents import AgentCoordinator
from session_manager import SessionManager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 初始化组件
try:
    llm_client = get_llm_client()
    logger.info(f"LLM客户端初始化成功: {Config.LLM_PROVIDER}")
except Exception as e:
    logger.error(f"LLM客户端初始化失败: {str(e)}")
    llm_client = None

agent_coordinator = AgentCoordinator(llm_client) if llm_client else None
session_manager = SessionManager()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API端点"""
    if not agent_coordinator:
        return jsonify({
            'error': 'LLM服务未初始化，请检查配置'
        }), 500
    
    try:
        data = request.json
        query = data.get('message', '')
        session_id = data.get('session_id', '')
        agent_type = data.get('agent_type', None)
        
        if not query:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 获取或创建会话
        if not session_id:
            session_id = session_manager.create_session()
        
        conversation_session = session_manager.get_session(session_id)
        
        # 获取对话上下文
        context = conversation_session.get_context()
        
        # 处理查询
        result = agent_coordinator.process(query, agent_type, context)
        
        # 保存消息到会话历史
        conversation_session.add_message('user', query)
        conversation_session.add_message('assistant', result['response'], result['agent_type'])
        
        return jsonify({
            'session_id': session_id,
            'agent': result['agent'],
            'agent_type': result['agent_type'],
            'response': result['response'],
            'provider': Config.LLM_PROVIDER
        })
    
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}")
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """获取可用智能体列表"""
    if not agent_coordinator:
        return jsonify({'error': 'LLM服务未初始化'}), 500
    
    return jsonify({
        'agents': agent_coordinator.get_agent_list()
    })


@app.route('/api/session/new', methods=['POST'])
def new_session():
    """创建新会话"""
    session_id = session_manager.create_session()
    return jsonify({'session_id': session_id})


@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """获取会话历史"""
    conversation_session = session_manager.get_session(session_id)
    return jsonify({
        'session_id': session_id,
        'messages': conversation_session.get_all_messages()
    })


@app.route('/api/session/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    """清空会话历史"""
    conversation_session = session_manager.get_session(session_id)
    conversation_session.clear()
    return jsonify({'message': '会话已清空'})


@app.route('/api/session/<session_id>/delete', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    success = session_manager.delete_session(session_id)
    if success:
        return jsonify({'message': '会话已删除'})
    return jsonify({'error': '会话不存在'}), 404


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    return jsonify({
        'provider': Config.LLM_PROVIDER,
        'model': getattr(Config, f'{Config.LLM_PROVIDER.upper()}_MODEL', 'unknown'),
        'active_sessions': session_manager.get_active_sessions_count(),
        'llm_initialized': llm_client is not None
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
