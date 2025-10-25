"""
Research Assistant Flask Application
A multi-agent research assistant using local and cloud LLMs
"""

from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import json
import uuid

# Import our custom modules
from agents.agent_manager import AgentManager
from llm.llm_manager import LLMManager
from utils.config import Config
from management.agent_manager import agent_manager as dynamic_agent_manager
from conversation.conversation_manager import ConversationManager, ConversationTurn

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize managers
config = Config()
llm_manager = LLMManager(config)
agent_manager = AgentManager(llm_manager)
conversation_manager = ConversationManager()

@app.route('/')
def index():
    """Main research assistant interface"""
    return render_template('index.html')

@app.route('/api/research', methods=['POST'])
def research():
    """Main research endpoint with conversation support"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        selected_agents = data.get('agents', [])
        selected_model = data.get('model', 'openai')
        selected_ollama_model = data.get('ollamaModel', None)
        selected_openai_model = data.get('openaiModel', None)
        selected_gemini_model = data.get('geminiModel', None)
        is_continuation = data.get('isContinuation', False)
        session_id = data.get('sessionId', None)
        deep_research_options = data.get('deepResearch', {})
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Create or get conversation session
        if is_continuation and session_id:
            # Continue existing session
            if session_id not in conversation_manager.sessions:
                return jsonify({'error': 'Session not found'}), 404
            conversation_manager.current_session_id = session_id
        else:
            # Start new session
            session_id = conversation_manager.create_new_session()
        
        # Get context from previous turns
        context = conversation_manager.get_session_context() if is_continuation else ""
        
        # Create conversation turn
        turn_id = str(uuid.uuid4())
        turn = ConversationTurn(
            turn_id=turn_id,
            query=query,
            agents=selected_agents,
            model=selected_model,
            ollama_model=selected_ollama_model,
            context=context
        )
        
        # Store query in session for context
        session['current_query'] = query
        session['research_start_time'] = datetime.now().isoformat()
        
        # Set preferred model for all agents
        for agent_name in selected_agents:
            try:
                agent = agent_manager.get_agent(agent_name)
                agent.set_preferred_provider(selected_model)
                
                # Update specific models based on selected provider
                if selected_model == 'ollama' and selected_ollama_model:
                    # Update the Ollama model in the LLM manager
                    llm_manager.providers['ollama'].model = selected_ollama_model
                elif selected_model == 'openai' and selected_openai_model:
                    # Update the OpenAI model in the LLM manager
                    llm_manager.providers['openai'].model = selected_openai_model
                elif selected_model == 'gemini' and selected_gemini_model:
                    # Update the Gemini model in the LLM manager
                    llm_manager.providers['gemini'].model = selected_gemini_model
            except:
                pass  # Agent not found, continue with default
        
        # Execute research using selected agents and model
        result = agent_manager.execute_research(query, selected_agents, selected_model, context, deep_research_options)
        
        # Update turn with results
        turn.result = result
        turn.summary = result.get('summary', '')
        
        # Add turn to conversation
        conversation_manager.add_turn_to_current_session(turn)
        
        return jsonify({
            'success': True,
            'query': query,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'sessionId': session_id,
            'turnId': turn_id,
            'isContinuation': is_continuation,
            'context': context
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama-models')
def get_ollama_models():
    """Get available Ollama models"""
    try:
        import requests
        ollama_url = config.get('OLLAMA_BASE_URL')
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            models = []
            for model in models_data.get('models', []):
                models.append({
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'modified': model.get('modified_at', ''),
                    'size_gb': round(model.get('size', 0) / (1024**3), 2)
                })
            return jsonify({
                'success': True,
                'models': models
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ollama API error: {response.status_code}',
                'models': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'models': []
        })

@app.route('/api/models')
def get_models():
    """Get available LLM models"""
    return jsonify({
        'models': llm_manager.get_available_models()
    })

@app.route('/api/conversation/new', methods=['POST'])
def new_conversation():
    """Start a new conversation session"""
    try:
        session_id = conversation_manager.create_new_session()
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/<session_id>')
def get_conversation(session_id):
    """Get conversation session details"""
    try:
        if session_id not in conversation_manager.sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = conversation_manager.export_session(session_id)
        return jsonify({
            'success': True,
            'session': session_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/<session_id>/export')
def export_conversation(session_id):
    """Export conversation session"""
    try:
        if session_id not in conversation_manager.sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = conversation_manager.export_session(session_id)
        return jsonify({
            'success': True,
            'session': session_data,
            'exported_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Agent Management API Endpoints
@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agents"""
    try:
        agents = dynamic_agent_manager.get_all_agents()
        return jsonify({
            'success': True,
            'agents': [agent.to_dict() for agent in agents]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get agents: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent_by_id(agent_id):
    """Get specific agent"""
    try:
        agent = dynamic_agent_manager.get_agent(agent_id)
        if agent:
            return jsonify({
                'success': True,
                'agent': agent.to_dict()
            })
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to get agent: {str(e)}'}), 500

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """Create new agent"""
    try:
        data = request.get_json()
        required_fields = ['name', 'description', 'icon', 'color', 'prompt_template']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        agent_id = dynamic_agent_manager.create_agent(
            name=data['name'],
            description=data['description'],
            icon=data['icon'],
            color=data['color'],
            prompt_template=data['prompt_template'],
            enabled=data.get('enabled', True)
        )
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'message': 'Agent created successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to create agent: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent"""
    try:
        data = request.get_json()
        
        # Only update provided fields
        update_data = {}
        allowed_fields = ['name', 'description', 'icon', 'color', 'prompt_template', 'enabled']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if dynamic_agent_manager.update_agent(agent_id, **update_data):
            return jsonify({
                'success': True,
                'message': 'Agent updated successfully'
            })
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to update agent: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete agent"""
    try:
        if dynamic_agent_manager.delete_agent(agent_id):
            return jsonify({
                'success': True,
                'message': 'Agent deleted successfully'
            })
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete agent: {str(e)}'}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates"""
    try:
        templates = dynamic_agent_manager.get_all_templates()
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500

@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get specific template"""
    try:
        template = dynamic_agent_manager.get_template(template_id)
        if template:
            return jsonify({
                'success': True,
                'template': template.to_dict()
            })
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to get template: {str(e)}'}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create new template"""
    try:
        data = request.get_json()
        required_fields = ['name', 'description', 'agents']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate agent IDs
        valid_agents = dynamic_agent_manager.validate_agent_ids(data['agents'])
        if not valid_agents:
            return jsonify({'error': 'No valid agents provided'}), 400
        
        template_id = dynamic_agent_manager.create_template(
            name=data['name'],
            description=data['description'],
            agents=valid_agents,
            enabled=data.get('enabled', True)
        )
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'Template created successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to create template: {str(e)}'}), 500

@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update template"""
    try:
        data = request.get_json()
        
        # Only update provided fields
        update_data = {}
        allowed_fields = ['name', 'description', 'agents', 'enabled']
        
        for field in allowed_fields:
            if field in data:
                if field == 'agents':
                    # Validate agent IDs
                    update_data[field] = dynamic_agent_manager.validate_agent_ids(data[field])
                else:
                    update_data[field] = data[field]
        
        if dynamic_agent_manager.update_template(template_id, **update_data):
            return jsonify({
                'success': True,
                'message': 'Template updated successfully'
            })
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to update template: {str(e)}'}), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete template"""
    try:
        if dynamic_agent_manager.delete_template(template_id):
            return jsonify({
                'success': True,
                'message': 'Template deleted successfully'
            })
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete template: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>/template-config', methods=['GET'])
def get_agent_template_config(agent_id):
    """Get template configuration for a specific agent"""
    try:
        config = dynamic_agent_manager.get_agent_template_config(agent_id)
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get template config: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>/template-config', methods=['PUT'])
def update_agent_template_config(agent_id):
    """Update template configuration for a specific agent"""
    try:
        data = request.get_json()
        
        if dynamic_agent_manager.update_agent_template_config(agent_id, data):
            return jsonify({
                'success': True,
                'message': 'Template configuration updated successfully'
            })
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to update template config: {str(e)}'}), 500

@app.route('/api/agent-management/metadata', methods=['GET'])
def get_agent_metadata():
    """Get agent management metadata"""
    try:
        metadata = dynamic_agent_manager.get_metadata()
        return jsonify({
            'success': True,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get metadata: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'available_agents': len(agent_manager.get_available_agents()),
        'available_models': len(llm_manager.get_available_models()),
        'active_sessions': len(conversation_manager.sessions)
    })

@app.route('/api/config/google')
def google_config():
    """Display Google API configuration (with masked sensitive data)"""
    google_api_key = config.get('GOOGLE_SEARCH_API_KEY', '')
    google_engine_id = config.get('GOOGLE_SEARCH_ENGINE_ID', '')
    gemini_api_key = config.get('GOOGLE_API_KEY', '')

    # Mask sensitive API keys (show first 8 chars + ... + last 4 chars)
    def mask_key(key):
        if not key:
            return 'Not set'
        if len(key) <= 12:
            return key
        return key[:8] + '...' + key[-4:]

    return jsonify({
        'google_search_api': {
            'api_key_configured': bool(google_api_key),
            'api_key_masked': mask_key(google_api_key),
            'engine_id_configured': bool(google_engine_id),
            'engine_id': google_engine_id,
            'search_provider': 'Google Custom Search API' if google_api_key and google_engine_id else 'DuckDuckGo (fallback)'
        },
        'google_gemini_api': {
            'api_key_configured': bool(gemini_api_key),
            'api_key_masked': mask_key(gemini_api_key),
            'model': config.get('GEMINI_MODEL', 'Not configured')
        },
        'timestamp': datetime.now().isoformat(),
        'note': 'API keys are masked for security. Use this endpoint for debugging only.'
    })

@app.route('/api/agents/<agent_id>/defaults')
def get_agent_defaults(agent_id):
    """Get default deep research options from agent template config"""
    try:
        template_config = dynamic_agent_manager.get_agent_template_config(agent_id)

        if not template_config:
            return jsonify({'error': 'Agent not found or no template config'}), 404

        # Convert template config to deep research options format
        defaults = {
            'enableDeepResearch': template_config.get('deep_research_enabled', False),
            'enableWebSearch': template_config.get('web_search_enabled', False),
            'searchEngine': template_config.get('search_engine', 'duckduckgo'),
            'searchResults': template_config.get('search_results_count', 10),
            'includeImages': template_config.get('include_images', False)
        }

        return jsonify({
            'agent_id': agent_id,
            'defaults': defaults,
            'template_config': template_config
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get agent defaults: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
