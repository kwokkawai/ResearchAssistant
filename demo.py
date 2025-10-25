"""
演示脚本 - 展示如何使用研究助手API
Demo script - Shows how to use the Research Assistant API
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"


def print_response(response):
    """格式化打印响应"""
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.status_code}")
        print(response.text)
    print()


def main():
    """主演示函数"""
    
    print("=" * 60)
    print("多智能体研究助手 API 演示")
    print("=" * 60)
    print()
    
    # 1. 检查系统状态
    print("1. 获取系统状态")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/api/status")
    print_response(response)
    
    # 2. 获取智能体列表
    print("2. 获取可用智能体列表")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/api/agents")
    print_response(response)
    
    # 3. 创建新会话
    print("3. 创建新会话")
    print("-" * 60)
    response = requests.post(f"{BASE_URL}/api/session/new")
    session_data = response.json()
    session_id = session_data.get('session_id')
    print(f"会话ID: {session_id}")
    print()
    
    # 4. 发送消息 - 研究问题（自动路由）
    print("4. 发送研究相关问题（自动路由）")
    print("-" * 60)
    message = {
        "message": "什么是定性研究方法？它与定量研究有什么区别？",
        "session_id": session_id
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=message,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    
    time.sleep(1)
    
    # 5. 发送消息 - 数据分析问题（指定智能体）
    print("5. 发送数据分析问题（指定数据分析智能体）")
    print("-" * 60)
    message = {
        "message": "如何选择合适的统计检验方法？",
        "session_id": session_id,
        "agent_type": "data"
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=message,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    
    time.sleep(1)
    
    # 6. 获取会话历史
    print("6. 获取会话历史")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/api/session/{session_id}/history")
    print_response(response)
    
    # 7. 清空会话
    print("7. 清空会话历史")
    print("-" * 60)
    response = requests.post(f"{BASE_URL}/api/session/{session_id}/clear")
    print_response(response)
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    print("注意: 此演示脚本需要Flask服务器正在运行")
    print("请先运行: python app.py")
    print()
    
    try:
        # 检查服务器是否运行
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        if response.status_code == 200:
            main()
        else:
            print("服务器未正常响应，请检查配置")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器")
        print("请确保Flask应用正在运行: python app.py")
    except Exception as e:
        print(f"错误: {str(e)}")
