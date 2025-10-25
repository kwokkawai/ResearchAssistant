// 应用状态
let sessionId = null;
let currentAgent = 'auto';
let isWaiting = false;

// 智能体图标映射
const agentIcons = {
    'research': '📚',
    'data': '📊',
    'writing': '✍️',
    'general': '💡',
    'auto': '🤖'
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    // 获取系统状态
    await updateStatus();
    
    // 加载智能体列表
    await loadAgents();
    
    // 创建新会话
    await createNewSession();
}

function setupEventListeners() {
    // 发送消息
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // 回车发送（Ctrl+Enter换行）
    document.getElementById('user-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 新建会话
    document.getElementById('new-session-btn').addEventListener('click', createNewSession);
    
    // 清空历史
    document.getElementById('clear-session-btn').addEventListener('click', clearSession);
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        document.getElementById('provider-status').textContent = 
            `提供商: ${data.provider} (${data.model})`;
        document.getElementById('session-count').textContent = 
            `活跃会话: ${data.active_sessions}`;
    } catch (error) {
        console.error('获取状态失败:', error);
    }
}

async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();
        
        const agentList = document.getElementById('agent-list');
        
        // 添加自动选择按钮（已在HTML中）
        
        // 添加其他智能体
        data.agents.forEach(agent => {
            const btn = createAgentButton(agent);
            agentList.appendChild(btn);
        });
    } catch (error) {
        console.error('加载智能体失败:', error);
    }
}

function createAgentButton(agent) {
    const btn = document.createElement('button');
    btn.className = 'agent-btn';
    btn.dataset.agent = agent.type;
    
    const icon = agentIcons[agent.type] || '🤖';
    
    btn.innerHTML = `
        <span class="agent-icon">${icon}</span>
        <div class="agent-info">
            <div class="agent-name">${agent.name}</div>
            <div class="agent-desc">${agent.description}</div>
        </div>
    `;
    
    btn.addEventListener('click', function() {
        selectAgent(agent.type, agent.name);
    });
    
    return btn;
}

function selectAgent(agentType, agentName) {
    currentAgent = agentType;
    
    // 更新按钮状态
    document.querySelectorAll('.agent-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-agent="${agentType}"]`).classList.add('active');
    
    // 更新显示
    document.getElementById('current-agent-display').textContent = 
        `当前助手: ${agentName}`;
}

async function createNewSession() {
    try {
        const response = await fetch('/api/session/new', {
            method: 'POST'
        });
        const data = await response.json();
        
        sessionId = data.session_id;
        
        // 清空消息显示
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>新会话已创建！</h2>
                <p>会话ID: ${sessionId.substring(0, 8)}...</p>
                <p>请输入您的问题开始对话...</p>
            </div>
        `;
        
        await updateStatus();
    } catch (error) {
        console.error('创建会话失败:', error);
        alert('创建会话失败，请重试');
    }
}

async function clearSession() {
    if (!sessionId) return;
    
    if (!confirm('确定要清空当前会话的历史记录吗？')) {
        return;
    }
    
    try {
        await fetch(`/api/session/${sessionId}/clear`, {
            method: 'POST'
        });
        
        // 清空消息显示
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>历史记录已清空！</h2>
                <p>请输入您的问题开始新的对话...</p>
            </div>
        `;
    } catch (error) {
        console.error('清空会话失败:', error);
        alert('清空会话失败，请重试');
    }
}

async function sendMessage() {
    if (isWaiting) return;
    
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 禁用输入
    isWaiting = true;
    input.disabled = true;
    document.getElementById('send-btn').disabled = true;
    
    // 显示用户消息
    appendMessage('user', message);
    
    // 清空输入框
    input.value = '';
    
    // 显示加载指示器
    const loadingId = showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                agent_type: currentAgent === 'auto' ? null : currentAgent
            })
        });
        
        if (!response.ok) {
            throw new Error('请求失败');
        }
        
        const data = await response.json();
        
        // 更新会话ID（如果是新会话）
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
        // 移除加载指示器
        removeTypingIndicator(loadingId);
        
        // 显示助手回复
        appendMessage('assistant', data.response, data.agent, data.agent_type);
        
        // 更新状态
        await updateStatus();
        
    } catch (error) {
        console.error('发送消息失败:', error);
        removeTypingIndicator(loadingId);
        appendMessage('assistant', '抱歉，处理您的请求时出现错误。请稍后重试。', '系统', 'error');
    } finally {
        // 恢复输入
        isWaiting = false;
        input.disabled = false;
        document.getElementById('send-btn').disabled = false;
        input.focus();
    }
}

function appendMessage(role, content, agentName = null, agentType = null) {
    const chatMessages = document.getElementById('chat-messages');
    
    // 移除欢迎消息
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    let headerHtml = '';
    if (role === 'user') {
        headerHtml = '<div class="message-header">👤 您</div>';
    } else if (role === 'assistant' && agentName) {
        const icon = agentIcons[agentType] || '🤖';
        headerHtml = `
            <div class="message-header">
                ${icon} ${agentName}
                <span class="agent-badge">${agentType}</span>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        ${headerHtml}
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const id = 'typing-' + Date.now();
    
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message assistant';
    typingDiv.innerHTML = `
        <div class="message-header">🤖 正在思考...</div>
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
